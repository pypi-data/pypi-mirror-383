"""
ComplexParams Handling
============================

Routines to post-process fitted or sampled parameter sets and compute
derived physical quantities.

This module provides the :class:`ComplexParams` class, which acts as a
bridge between raw fitting/sampling outputs (parameter vectors) and
scientifically useful quantities such as line fluxes, widths, equivalent
widths, luminosities, and single-epoch black hole mass estimators.

Main Features
-------------
- Unified interface to handle both:
  * **single best-fit parameters** (deterministic optimization), and
  * **sampled parameters** (Monte Carlo / MCMC posterior draws).
- Automatic grouping of parameters by spectral region and profile.
- Computation of:
  * line flux, FWHM, velocity width (km/s),
  * line centers, amplitudes, shape parameters,
  * equivalent width (EQW),
  * monochromatic and bolometric luminosities,
  * combined quantities (e.g. Hα+Hβ, Mg II+Fe, CIV blends).
- uncertainties propagation via :mod:`uncertainties`.

Public API
----------
- :class:`ComplexParams`:
    High-level handler that connects a :class:`ComplexSampler` result
    to physical parameter extraction.

Typical Workflow
----------------
1. Fit or sample spectra with :class:`RegionFitting` or a sampler.
2. Wrap the result in a :class:`ComplexSampler` instance.
3. Construct :class:`ComplexParams(samplerclass)` from it.
4. Call :meth:`ComplexParams.extract_params` to obtain dictionaries
    of physical line quantities, optionally summarized across samples.

Notes
-----
- The attribute ``method`` determines whether results are handled as
    ``"single"`` (best fit) or ``"sampled"`` (posterior draws).
- Many helpers internally rely on
    :func:`make_batch_fwhm_split[_with_error]`,
    :func:`make_integrator`, and profile-specific shape functions.
"""

__author__ = 'felavila'

__all__ = [
    "ComplexParams",
]
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np 
import jax.numpy as jnp 
from jax import vmap
#from auto_uncertainties import Uncertainty
from uncertainties import unumpy

from collections import defaultdict

from sheap.Profiles.Profiles import PROFILE_LINE_FUNC_MAP,PROFILE_FUNC_MAP
from sheap.Profiles.Utils import make_integrator
from sheap.Utils.Constants import c
from sheap.ComplexParams.Utils.fwhm_conv import make_batch_fwhm_split,make_batch_fwhm_split_with_error
from sheap.ComplexParams.Utils.Physical_functions import calc_fwhm_kms,calc_luminosity,calc_monochromatic_luminosity,calc_bolometric_luminosity,extra_params_functions
from sheap.ComplexParams.Utils.After_fit_profile_helpers import integrate_batch_with_error,evaluate_with_error 
from sheap.ComplexParams.Utils.Combine_profiles import combine_components,combine_fastspecfit,combine_pyqsofit,combine_pyqsofit_single
from sheap.ComplexParams.Utils.Sample_handlers import pivot_and_split,summarize_nested_samples,concat_dicts

#TODO add hyper parameter "raw" that gives exactly the params like dict params. 
class ComplexParams:
    def __init__(self, samplerclass: "ComplexSampler"):
        self.samplerclass = samplerclass
        self.model = samplerclass.model
        self.c = samplerclass.c
        self.dependencies = samplerclass.dependencies
        self.scale = samplerclass.scale
        self.spectra= samplerclass.spectra
        self.mask = samplerclass.mask
        self.d = samplerclass.d
        
        
        self.names = samplerclass.names 
        self.complex_class = samplerclass.complex_class
        self.constraints = samplerclass.constraints
        
        self.params_dict = samplerclass.params_dict
        self.params = samplerclass.params
        self.uncertainty_params = samplerclass.uncertainty_params
        self.method = samplerclass.method
        if not self.method:
            print("Not found method sampler")
            self.method = "single"
        
        self.BOL_CORRECTIONS = samplerclass.BOL_CORRECTIONS
        self.SINGLE_EPOCH_ESTIMATORS = samplerclass.SINGLE_EPOCH_ESTIMATORS
        self.wavelength_grid = jnp.linspace(0, 20_000, 20_000)
        self.LINES_TO_COMBINE = ["Halpha", "Hbeta","MgII","CIV"]
        self.limit_velocity = 150.
    
    def extract_params(self,full_samples=None,idx_obj=None,summarize=False):
        #Add the filtering an separation of the params for params_single and the sample reduction for params_sampled
        if self.method == "single":
            if summarize:
                return pivot_and_split(self.names,self._extract_basic_params_single())
            return self._extract_basic_params_single()
        else:
            #if summarize:
                #print("Samples will be summarize")
            return summarize_nested_samples(self._extract_basic_params_sampled(full_samples=full_samples,idx_obj=idx_obj),run_summarize=summarize)

    def _extract_basic_params_sampled(self, full_samples, idx_obj):
        """
        Extract line quantities (flux, FWHM, center, etc.) from posterior samples.
        Designed for use with MCMC or MC draws.
        """
        
        basic_params: Dict[str, Dict[str, np.ndarray]] = {}
        complex_class_group_by_region = self.complex_class.group_by("region")
        cont_group = complex_class_group_by_region["continuum"]
        idx_cont = cont_group.flat_param_indices_global
        cont_params = full_samples[:, idx_cont]
        distances = np.full((full_samples.shape[0],), self.d[idx_obj], dtype=np.float64)

        for region, region_group in complex_class_group_by_region.items():
            if region in ("fe", "continuum", "host"):
                continue

            line_names, components = [], []
            flux_parts, fwhm_parts = [], []
            fwhm_kms_parts, center_parts = [], []
            amp_parts, eqw_parts, lum_parts = [], [], []
            shape_params_list = []

            region_group_by_profile = region_group.group_by("profile_name")

            for profile_name, prof_group in region_group_by_profile.items():
                if "_" in profile_name:
                    _, subprof = profile_name.split("_", 1)
                    profile_fn = PROFILE_LINE_FUNC_MAP[subprof]
                    batch_fwhm = make_batch_fwhm_split(subprof)
                    integrator = make_integrator(profile_fn, method="vmap")

                    (
                        _line_names, _components, _flux, _fwhm, _fwhm_kms,
                        _centers, _amps, _eqw, _lum, _shapes
                    ) = self._accumulate_spaf_sampled(
                        prof_group, profile_fn, batch_fwhm, integrator, cont_params, full_samples
                    )

                else:
                    profile_fn = PROFILE_LINE_FUNC_MAP[profile_name]
                    batch_fwhm = make_batch_fwhm_split(profile_name)
                    integrator = make_integrator(profile_fn, method="vmap")

                    idxs = prof_group.flat_param_indices_global
                    params = full_samples[:, idxs]

                    _line_names = [l.line_name for l in prof_group.lines]
                    _components = [l.component for l in prof_group.lines]
                    params_by_line = params.reshape(params.shape[0], -1, profile_fn.n_params)

                    amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals = self._extract_sampled_profile_quantities(
                        profile_fn, integrator, batch_fwhm, params_by_line, cont_params, distances
                    )

                    _flux, _fwhm, _fwhm_kms = [flux], [fwhm], [fwhm_kms]
                    _centers, _amps, _eqw, _lum = [centers], [amps], [eqw], [lum_vals]
                    _shapes = [{k: v for k, v in zip(profile_fn.param_names[2:], shape_params.T)}]

                line_names.extend(_line_names)
                components.extend(_components)
                flux_parts.extend(_flux)
                fwhm_parts.extend(_fwhm)
                fwhm_kms_parts.extend(_fwhm_kms)
                center_parts.extend(_centers)
                amp_parts.extend(_amps)
                eqw_parts.extend(_eqw)
                lum_parts.extend(_lum)
                shape_params_list.extend(_shapes)

            basic_params[region] = {"lines": line_names,
                "component": components,
                "flux": np.concatenate(flux_parts, axis=1),
                "fwhm": np.concatenate(fwhm_parts, axis=1),
                "fwhm_kms": np.concatenate(fwhm_kms_parts, axis=1),
                "center": np.concatenate(center_parts, axis=1),
                "amplitude": np.concatenate(amp_parts, axis=1),
                "eqw": np.concatenate(eqw_parts, axis=1),
                "luminosity": np.concatenate(lum_parts, axis=1),
                "shape_params": concat_dicts(shape_params_list) 
            }
        


        # basic_params["broad"].update({"MgII":combine_fastspecfit(self.spectra[[idx_obj],0,:],self.spectra[[idx_obj],1,:],full_samples,
        #                                                         {"MgII"},basic_params["broad"],
        #                                                     complex_class_group_by_region)})
        flux_fe = 0 
        if "fe" in complex_class_group_by_region.keys():
            group_fe = complex_class_group_by_region["fe"]
            profile_fe = group_fe.combined_profile
            idx_fe_params = group_fe.flat_param_indices_global
            params_fe = full_samples[:,idx_fe_params]
            wavelength_grid_fe = jnp.linspace(2200,3090, 1_000) #maybe to small the grid.
            integrator_fe = make_integrator(profile_fe, method="vmap")
            flux_fe = integrator_fe(wavelength_grid_fe, params_fe[:,None,:])
            basic_params["broad"]["extras"] = {"R_Fe":flux_fe}
        
        wl_i = self.spectra[idx_obj, 0, :]
        mask_i = self.mask[idx_obj, :]
        L_w, L_bol,F_cont = {}, {},{}
        for wave in map(float, self.BOL_CORRECTIONS.keys()):
            wstr = str(int(wave))
            if (jnp.isclose(wl_i, wave, atol=2) & ~mask_i).any():
                Fcont = vmap(cont_group.combined_profile, in_axes=(None, 0))(jnp.array([wave]), cont_params).squeeze()
                Lmono = calc_monochromatic_luminosity(distances, Fcont, wave)
                Lbolval = calc_bolometric_luminosity(Lmono, self.BOL_CORRECTIONS[wstr])
                L_w[wstr], L_bol[wstr],F_cont[wstr] = np.array(Lmono), np.array(Lbolval), np.array(Fcont)     
        
        
        combined = combine_components(basic_params, cont_group, cont_params, distances,
                                      LINES_TO_COMBINE=self.LINES_TO_COMBINE,
                                      limit_velocity=self.limit_velocity,c=self.c,ucont_params=None,flux_fe=flux_fe)
        
        combined_pyqso = {line: combine_pyqsofit(basic_params["broad"],complex_class_group_by_region,line,full_samples,distances,flux_fe) for line in basic_params["broad"]["lines"] if line in [ "Halpha","Hbeta","MgII","CIV"]}
        
        result = {"basic_params": basic_params, "L_w": L_w, "L_bol": L_bol,"F_cont":F_cont, "combine_params": combined,"combined_pyqso":combined_pyqso}
        
        
        for k in ["basic_params","combine_params","combined_pyqso"]:
            if k == "basic_params":
                result_local = result[k]["broad"]
            else:
                result_local = result[k]
            #print(extra_params_functions(result_local,L_w,L_bol,self.SINGLE_EPOCH_ESTIMATORS,self.c))
            result.update({f"extra_{k}": extra_params_functions(result_local,L_w,L_bol,self.SINGLE_EPOCH_ESTIMATORS,self.c)}) #extras could be added directly because the are not related to the combination.
        
        return result
    
    
    def _extract_basic_params_single(self):
        basic_params: Dict[str, Dict[str, np.ndarray]] = {}
        distances = self.d.copy()
        complex_class_group_by_region = self.complex_class.group_by("region")
        cont_group = complex_class_group_by_region["continuum"]
        idx_cont = cont_group.flat_param_indices_global
        cont_params = self.params[:, idx_cont]
        ucont_params = self.uncertainty_params[:, idx_cont]

        for region, region_group in complex_class_group_by_region.items():
            if region in ("fe", "continuum", "host"):
                continue

            line_names, components = [], []
            flux_parts, fwhm_parts, fwhm_kms_parts = [], [], []
            center_parts, amp_parts, eqw_parts, lum_parts = [], [], [], []
            shape_params_list = []

            region_group_by_profile = region_group.group_by("profile_name")

            for profile_name, prof_group in region_group_by_profile.items():
                if "_" in profile_name:  # SPAF or template Fe
                    _, subprof = profile_name.split("_", 1)
                    profile_fn = PROFILE_LINE_FUNC_MAP[subprof]
                    batch_fwhm = make_batch_fwhm_split_with_error(subprof)

                    (_line_names, _components, _flux, _fwhm, _fwhm_kms,_centers, _amps, _eqw, _lum, _shapes) = self._accumulate_spaf_components(prof_group, profile_fn, batch_fwhm, cont_params, ucont_params)

                else:
                    profile_fn = PROFILE_LINE_FUNC_MAP[profile_name]
                    batch_fwhm = make_batch_fwhm_split_with_error(profile_name)

                    idxs = prof_group.flat_param_indices_global
                    _params = self.params[:, idxs]
                    _uparams = self.uncertainty_params[:, idxs]

                    _line_names = [l.line_name for l in prof_group.lines]
                    _components = [l.component for l in prof_group.lines]

                    params_by_line = _params.reshape(_params.shape[0], -1, profile_fn.n_params)
                    uparams_by_line = _uparams.reshape(_uparams.shape[0], -1, profile_fn.n_params)

                    amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals = self._extract_profile_quantities(
                        profile_fn, batch_fwhm, params_by_line, uparams_by_line, cont_params, ucont_params)

                    _flux, _fwhm, _fwhm_kms = [flux], [fwhm], [fwhm_kms]
                    _centers, _amps, _eqw, _lum = [centers], [amps], [eqw], [lum_vals]
                    _shapes = [{k: v for k, v in zip(profile_fn.param_names[2:], shape_params.T)}]
                line_names.extend(_line_names)
                components.extend(_components)
                flux_parts.extend(_flux)
                fwhm_parts.extend(_fwhm)
                fwhm_kms_parts.extend(_fwhm_kms)
                center_parts.extend(_centers)
                amp_parts.extend(_amps)
                eqw_parts.extend(_eqw)
                lum_parts.extend(_lum)
                shape_params_list.extend(_shapes)

            basic_params[region] = {
                "lines": line_names,
                "component": components,
                "flux": np.concatenate(flux_parts, axis=1),
                "fwhm": np.concatenate(fwhm_parts, axis=1),
                "fwhm_kms": np.concatenate(fwhm_kms_parts, axis=1),
                "center": np.concatenate(center_parts, axis=1),
                "amplitude": np.concatenate(amp_parts, axis=1),
                "eqw": np.concatenate(eqw_parts, axis=1),
                "luminosity": np.concatenate(lum_parts, axis=1),
                "shape_params": concat_dicts(shape_params_list) 
            }
        
        #combine_pyqsofit_single
        # basic_params["broad"].update({"MgII":combine_fastspecfit(self.spectra[:,0,:],self.spectra[:,1,:],None,
        #                                                         {"MgII"},basic_params["broad"],
        #                                                     complex_class_group_by_region)})
        flux_fe = 1.
        if "fe" in complex_class_group_by_region.keys():
             group_fe = complex_class_group_by_region["fe"]
             combine_profile_fe = group_fe.combined_profile
             params_fe = group_fe.params[:, None, :]
             uparams_fe = group_fe.uncertainty_params[:, None, :]
             wavelength_grid_fe = jnp.linspace(2200,3090, 1_000)  
             flux_fe =  unumpy.uarray(*np.array(integrate_batch_with_error(combine_profile_fe,wavelength_grid_fe,params_fe,uparams_fe))) 
             basic_params["broad"]["extras"] = {"R_Fe":flux_fe}

        #from here can be the same function only take care on the uncertainty params of the continuum
        L_w, L_bol,F_cont = {}, {},{}
        for wave in map(float, self.BOL_CORRECTIONS.keys()):
            wstr = str(int(wave))
            hits = jnp.isclose(self.spectra[:, 0, :], wave, atol=2)
            valid = np.array((hits & (~self.mask)).any(axis=1, keepdims=True))

            if any(valid):
                x = jnp.full((cont_params.shape[0], 1), wave)
                Fcont = unumpy.uarray(*np.array(
                    evaluate_with_error(cont_group.combined_profile, x, cont_params, jnp.zeros_like(x), ucont_params)
                )) * valid.astype(float)
                #print(valid)
                Lmono = calc_monochromatic_luminosity(np.array(distances[:, None]), Fcont, wave)
                Lbolval = calc_bolometric_luminosity(Lmono, self.BOL_CORRECTIONS[wstr])
                L_w[wstr], L_bol[wstr],F_cont[wstr] = Lmono, Lbolval,Fcont
       
        #maybe is best just combine witouth take in consideration the errors?
        combined = combine_components(basic_params, cont_group, cont_params, distances,
                                      LINES_TO_COMBINE=self.LINES_TO_COMBINE,limit_velocity=self.limit_velocity,
                                      c=self.c,ucont_params=ucont_params,flux_fe=flux_fe)
        
        combined_pyqso = {line: combine_pyqsofit_single(basic_params["broad"],complex_class_group_by_region,line,distances,flux_fe) for line in basic_params["broad"]["lines"] if line in [ "Halpha","Hbeta","MgII","CIV"]}
        
        result = {"basic_params": basic_params, "L_w": L_w, "L_bol": L_bol,"F_cont":F_cont, "combine_params": combined,"combined_pyqso":combined_pyqso}
        
        
        for k in ["basic_params","combine_params","combined_pyqso"]:
             if k == "basic_params":
                 result_local = result[k]["broad"]
             else:
                 result_local = result[k]
             #print(extra_params_functions(result_local,L_w,L_bol,self.SINGLE_EPOCH_ESTIMATORS,self.c))
             result.update({f"extra_{k}": extra_params_functions(result_local,L_w,L_bol,self.SINGLE_EPOCH_ESTIMATORS,self.c)}) #extras could be added directly because the are not related to the combination.
        return result
    ###########################SINGLE########################################
    def _accumulate_spaf_components(self, prof_group, profile_fn, batch_fwhm, cont_params, ucont_params):
        
        all_flux, all_fwhm, all_fwhm_kms = [], [], []
        all_centers, all_amps, all_eqws, all_lums = [], [], [], []
        all_line_names, all_components, all_shape_dicts = [], [], []
        #for sub_prof_gropu in 
        params_names = prof_group._master_param_names
        for sp,idx_params in zip(prof_group.lines,prof_group.global_profile_params_index_list,):
            params_by_line, uparams_by_line = self._build_spaf_param_matrices(sp,idx_params,params_names)
            
            amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals = self._extract_profile_quantities(profile_fn, batch_fwhm, params_by_line, uparams_by_line, cont_params, ucont_params)
            all_flux.append(flux)
            all_fwhm.append(fwhm)
            all_fwhm_kms.append(fwhm_kms)
            all_centers.append(centers)
            all_amps.append(amps)
            all_eqws.append(eqw)
            all_lums.append(lum_vals)
            all_line_names.extend(sp.region_lines)
            all_components.extend([sp.component] * params_by_line.shape[1])
            all_shape_dicts.append({k: v for k, v in zip(profile_fn.param_names[2:], shape_params.T)})

        return (
            all_line_names, all_components, all_flux, all_fwhm, all_fwhm_kms,
            all_centers, all_amps, all_eqws, all_lums, all_shape_dicts
        )
                 
    def _build_spaf_param_matrices(self,sp,idx_params,params_names):
        
        full_params_by_line = []
        ufull_params_by_line = []
        _params = self.params[:, idx_params]
        _uncertainty_params = self.uncertainty_params[:, idx_params]
        names = np.array(params_names)[idx_params]
        
        amplitude_relations = sp.amplitude_relations
        amplitude_index = [i for i, name in enumerate(names) if "logamp" in name]
        ind_amplitude_index = {i[2] for i in amplitude_relations}
        dic_amp = {i: ii for i, ii in zip(ind_amplitude_index, amplitude_index)}
        idx_shift = max(amplitude_index) + 1
        for i,(_, factor, idx) in enumerate(amplitude_relations):
            amp = _params[:, [dic_amp[idx]]] + np.log10(factor)
            uamp = _uncertainty_params[:, [dic_amp[idx]]]
            center = sp.center[i] + _params[:, [idx_shift]]
            ucenter = _uncertainty_params[:, [idx_shift]]
            extras = _params[:, idx_shift+1:]
            uextras = _uncertainty_params[:, idx_shift+1:]
            full_params_by_line.append(np.column_stack([amp, center, extras]))
            ufull_params_by_line.append(np.column_stack([uamp, ucenter, uextras]))
        return np.moveaxis(np.array(full_params_by_line), 0, 1), np.moveaxis(np.array(ufull_params_by_line), 0, 1)

    def _extract_profile_quantities(self, profile_fn, batch_fwhm, params_by_line, uparams_by_line, cont_params, ucont_params):
        amps = 10**unumpy.uarray(params_by_line[:,:,0], uparams_by_line[:,:,0])
        centers = unumpy.uarray(params_by_line[:,:,1], uparams_by_line[:,:,1])
        shape_params = unumpy.uarray(params_by_line[:,:,2:], uparams_by_line[:,:,2:])
        flux =  unumpy.uarray(*np.array(integrate_batch_with_error(profile_fn,self.wavelength_grid,params_by_line,uparams_by_line))) 
        
        fwhm = unumpy.uarray(*np.array(batch_fwhm(unumpy.nominal_values(amps), unumpy.nominal_values(centers), unumpy.nominal_values(shape_params),
                                                  unumpy.std_devs(amps), unumpy.std_devs(centers), unumpy.std_devs(shape_params))))
        
        fwhm_kms = calc_fwhm_kms(fwhm, np.array(self.c), centers)
        cont_vals = unumpy.uarray(*np.array(
            evaluate_with_error(self.complex_class.group_by("region")["continuum"].combined_profile,
                                unumpy.nominal_values(centers), cont_params, unumpy.std_devs(centers), ucont_params)))
        
        eqw = flux / cont_vals
        lum_vals = calc_luminosity(np.array(self.d[:, None]), flux)

        return amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals
    
    
    
    ############SAMPLED###############################################
    def _accumulate_spaf_sampled(self, prof_group, profile_fn, batch_fwhm, integrator_fn, cont_params, full_samples):
        all_flux, all_fwhm, all_fwhm_kms = [], [], []
        all_centers, all_amps, all_eqws, all_lums = [], [], [], []
        all_line_names, all_components, all_shape_dicts = [], [], []
        params_names = prof_group._master_param_names
        
        for sp,idx_param in zip(prof_group.lines,prof_group.global_profile_params_index_list,):
            params_by_line = self._build_spaf_sampled_params(sp,idx_param,params_names,full_samples)
            amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals = self._extract_sampled_profile_quantities(
                profile_fn, integrator_fn, batch_fwhm, params_by_line, cont_params, np.full((full_samples.shape[0],), self.d[0])
            )

            all_flux.append(flux)
            all_fwhm.append(fwhm)
            all_fwhm_kms.append(fwhm_kms)
            all_centers.append(centers)
            all_amps.append(amps)
            all_eqws.append(eqw)
            all_lums.append(lum_vals)
            all_line_names.extend(sp.region_lines)
            all_components.extend([sp.component] * params_by_line.shape[1])
            all_shape_dicts.append({k: v for k, v in zip(profile_fn.param_names[2:], shape_params.T)})

        return (
            all_line_names, all_components, all_flux, all_fwhm, all_fwhm_kms,
            all_centers, all_amps, all_eqws, all_lums, all_shape_dicts
        )           
    def _build_spaf_sampled_params(self,sp,idx_param,params_names, full_samples):
    
        params = full_samples[:, idx_param]
        names = np.array(params_names)[idx_param]
        
        amplitude_relations = sp.amplitude_relations
        idx_pos = np.where(["logamp" in n for n in names])[0]
        amplitude_index = [i for i, name in enumerate(names) if "logamp" in name]
        ind_amplitude_index = {i[2] for i in amplitude_relations}
        dic_amp = {i: ii for i, ii in zip(ind_amplitude_index, amplitude_index)}
        idx_shift = idx_pos.max() + 1

        full_params_by_line = []
        for i,(_,factor,idx) in enumerate(amplitude_relations):
            amp = params[:, [dic_amp[idx]]] + np.log10(factor)
            center = (sp.center[i]+params[:,[idx_shift]])
            extras = (params[:,idx_shift+1:])
            full_params_by_line.append(np.column_stack([amp, center, extras]))

        return np.moveaxis(np.array(full_params_by_line), 0, 1)
    
    def _extract_sampled_profile_quantities(self, profile_fn, integrator_fn, batch_fwhm, params_by_line, cont_params, distances):
        amps = 10**params_by_line[:, :, 0]
        centers = params_by_line[:, :, 1]
        shape_params = jnp.abs(params_by_line[:, :, 2:])

        flux = integrator_fn(self.wavelength_grid, params_by_line)
        fwhm = batch_fwhm(amps, centers, shape_params)
        fwhm_kms = jnp.abs(calc_fwhm_kms(fwhm, self.c, centers))

        cont_vals = vmap(self.complex_class.group_by("region")["continuum"].combined_profile, in_axes=(0, 0))(centers, cont_params)
        eqw = flux / cont_vals
        lum_vals = calc_luminosity(distances[:, None], flux)

        return amps, centers, shape_params, flux, fwhm, fwhm_kms, eqw, lum_vals

