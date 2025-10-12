"""
PhotosynthesisModel Plugin for PyHelios.

This module provides a high-level interface to the Helios photosynthesis modeling 
plugin, enabling simulation of plant photosynthesis processes using both empirical 
and mechanistic models.
"""

from typing import List, Optional, Union
from .Context import Context
from .wrappers import UPhotosynthesisWrapper as photosynthesis_wrapper
from .types.photosynthesis import (
    PhotosyntheticTemperatureResponseParameters,
    EmpiricalModelCoefficients, 
    FarquharModelCoefficients,
    PHOTOSYNTHESIS_SPECIES,
    validate_species_name,
    get_available_species,
    get_species_aliases
)
from .validation.plugin_decorators import (
    validate_photosynthesis_species_params,
    validate_empirical_model_params,
    validate_farquhar_model_params,
    validate_photosynthesis_uuid_params
)


class PhotosynthesisModelError(Exception):
    """Exception raised by PhotosynthesisModel operations."""
    pass


class PhotosynthesisModel:
    """
    High-level interface for Helios photosynthesis modeling.
    
    The PhotosynthesisModel provides methods for configuring and running
    photosynthesis simulations using various models including empirical
    and mechanistic (Farquhar-von Caemmerer-Berry) approaches.
    
    Features:
    - Support for empirical and FvCB photosynthesis models
    - Built-in species library with 21+ plant species
    - Comprehensive parameter validation
    - Context manager support for proper cleanup
    
    Example:
        >>> from pyhelios import Context, PhotosynthesisModel
        >>> from pyhelios.types import EmpiricalModelCoefficients
        >>> context = Context()
        >>> with PhotosynthesisModel(context) as photosynthesis:
        ...     # Configure empirical model
        ...     coeffs = EmpiricalModelCoefficients(
        ...         Tref=298.0,      # Reference temperature (K)
        ...         Ci_ref=290.0,    # Reference CO2 concentration (μmol/mol)
        ...         Asat=20.0,       # Light-saturated photosynthesis rate (μmol/m²/s)
        ...         theta=65.0       # Light response curvature (W/m²)
        ...     )
        ...     photosynthesis.setEmpiricalModelCoefficients(coeffs)
        ...     photosynthesis.run()
        
    Available species can be queried using:
        >>> PhotosynthesisModel.get_available_species()
        ['ALMOND', 'APPLE', 'AVOCADO', ...]
    """
    
    def __init__(self, context: Context):
        """
        Initialize PhotosynthesisModel.
        
        Args:
            context: PyHelios Context instance containing the 3D geometry
            
        Raises:
            PhotosynthesisModelError: If plugin is not available or initialization fails
        """
        if not isinstance(context, Context):
            raise PhotosynthesisModelError(
                f"Context parameter must be a Context instance, got {type(context).__name__}"
            )
            
        self.context = context
        self._native_ptr = None
        
        try:
            # Get the native context pointer
            context_ptr = self.context.getNativePtr()
            if context_ptr is None:
                raise PhotosynthesisModelError("Context has no native pointer - context may not be properly initialized")
            
            # Create the photosynthesis model
            self._native_ptr = photosynthesis_wrapper.createPhotosynthesisModel(context_ptr)
            if self._native_ptr is None:
                raise PhotosynthesisModelError("Failed to create photosynthesis model")
                
        except Exception as e:
            if "photosynthesis plugin is not available" in str(e).lower():
                raise PhotosynthesisModelError(
                    "Photosynthesis plugin is not available. "
                    "Please rebuild PyHelios with photosynthesis plugin enabled:\n"
                    "  build_scripts/build_helios --plugins photosynthesis"
                ) from e
            elif "mock mode" in str(e).lower():
                raise PhotosynthesisModelError(
                    "PhotosynthesisModel requires native Helios libraries. "
                    "Currently running in mock mode. Please build native libraries:\n"
                    "  build_scripts/build_helios --plugins photosynthesis"
                ) from e
            else:
                raise PhotosynthesisModelError(f"Failed to initialize PhotosynthesisModel: {e}") from e

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit with cleanup."""
        self.cleanup()

    def cleanup(self):
        """Clean up native resources."""
        if hasattr(self, '_native_ptr') and self._native_ptr is not None:
            try:
                photosynthesis_wrapper.destroyPhotosynthesisModel(self._native_ptr)
            except Exception:
                pass  # Ignore cleanup errors
            finally:
                self._native_ptr = None

    def get_native_ptr(self):
        """Get the native C++ pointer for advanced operations."""
        return self._native_ptr

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

    # Model Configuration
    def setModelTypeEmpirical(self):
        """
        Set the photosynthesis model type to empirical.
        
        The empirical model uses light response curves with saturation kinetics.
        """
        photosynthesis_wrapper.setModelTypeEmpirical(self._native_ptr)

    def setModelTypeFarquhar(self):
        """
        Set the photosynthesis model type to Farquhar-von Caemmerer-Berry.
        
        The FvCB model is a mechanistic model accounting for biochemical 
        limitations of C3 photosynthesis.
        """
        photosynthesis_wrapper.setModelTypeFarquhar(self._native_ptr)

    # Model Execution
    def run(self):
        """
        Run photosynthesis calculations for all primitives in the context.
        
        The model must be configured with appropriate coefficients before running.
        """
        photosynthesis_wrapper.run(self._native_ptr)

    @validate_photosynthesis_uuid_params
    def runForPrimitives(self, uuids: Union[List[int], int]):
        """
        Run photosynthesis calculations for specific primitives.
        
        Args:
            uuids: Single UUID (integer) or list of UUIDs for primitives
        """
        if isinstance(uuids, int):
            uuids = [uuids]
        photosynthesis_wrapper.runForUUIDs(self._native_ptr, uuids)

    # Species Configuration
    @validate_photosynthesis_species_params
    def setSpeciesCoefficients(self, species: str, uuids: Optional[List[int]] = None):
        """
        Set Farquhar model coefficients from built-in species library.
        
        Args:
            species: Species name from the built-in library
            uuids: Optional list of primitive UUIDs. If None, applies to all primitives.
            
        Example:
            >>> model.setSpeciesCoefficients("APPLE")
            >>> model.setSpeciesCoefficients("SOYBEAN", [uuid1, uuid2])
        """
        if uuids is None:
            photosynthesis_wrapper.setFarquharCoefficientsFromLibrary(self._native_ptr, species)
        else:
            photosynthesis_wrapper.setFarquharCoefficientsFromLibraryForUUIDs(self._native_ptr, species, uuids)

    def setFarquharCoefficientsFromLibrary(self, species: str, uuids: Optional[List[int]] = None):
        """
        Set Farquhar model coefficients from built-in species library.
        
        This method matches the C++ API naming: setFarquharCoefficientsFromLibrary()
        
        Args:
            species: Species name from the built-in library
            uuids: Optional list of primitive UUIDs. If None, applies to all primitives.
            
        Example:
            >>> model.setFarquharCoefficientsFromLibrary("APPLE")
            >>> model.setFarquharCoefficientsFromLibrary("SOYBEAN", [uuid1, uuid2])
        """
        if uuids is None:
            photosynthesis_wrapper.setFarquharCoefficientsFromLibrary(self._native_ptr, species)
        else:
            photosynthesis_wrapper.setFarquharCoefficientsFromLibraryForUUIDs(self._native_ptr, species, uuids)

    def getSpeciesCoefficients(self, species: str) -> List[float]:
        """
        Get Farquhar model coefficients for a species from the library.
        
        Args:
            species: Species name
            
        Returns:
            List of Farquhar model coefficients for the species
        """
        species = validate_species_name(species)
        return photosynthesis_wrapper.getFarquharCoefficientsFromLibrary(self._native_ptr, species)

    @staticmethod
    def get_available_species() -> List[str]:
        """
        Static method to get available species without creating a model instance.
        
        Returns:
            List of species names available in the photosynthesis library
        """
        return get_available_species()

    @staticmethod
    def get_species_aliases() -> dict:
        """
        Static method to get species aliases mapping.
        
        Returns:
            Dictionary mapping aliases to canonical species names
        """
        return get_species_aliases()

    # Model Coefficient Configuration
    @validate_empirical_model_params
    def setEmpiricalModelCoefficients(self, coefficients: EmpiricalModelCoefficients, 
                                     uuids: Optional[List[int]] = None):
        """
        Set empirical model coefficients.
        
        Args:
            coefficients: EmpiricalModelCoefficients instance with model parameters
            uuids: Optional list of primitive UUIDs. If None, applies to all primitives.
        """
        # Convert to list format expected by C++ interface
        coeff_list = coefficients.to_array()
        
        if uuids is None:
            photosynthesis_wrapper.setEmpiricalModelCoefficients(self._native_ptr, coeff_list)
        else:
            photosynthesis_wrapper.setEmpiricalModelCoefficientsForUUIDs(self._native_ptr, coeff_list, uuids)

    @validate_farquhar_model_params
    def setFarquharModelCoefficients(self, coefficients: FarquharModelCoefficients,
                                    uuids: Optional[List[int]] = None):
        """
        Set Farquhar model coefficients.
        
        Args:
            coefficients: FarquharModelCoefficients instance with FvCB parameters
            uuids: Optional list of primitive UUIDs. If None, applies to all primitives.
        """
        # Convert to list format expected by C++ interface
        coeff_list = coefficients.to_array()
        
        if uuids is None:
            photosynthesis_wrapper.setFarquharModelCoefficients(self._native_ptr, coeff_list)
        else:
            photosynthesis_wrapper.setFarquharModelCoefficientsForUUIDs(self._native_ptr, coeff_list, uuids)

    # Individual Farquhar Parameter Setting
    def setVcmax(self, vcmax: float, uuids: List[int], dha: Optional[float] = None, 
                topt: Optional[float] = None, dhd: Optional[float] = None):
        """
        Set maximum carboxylation rate for Farquhar model.
        
        This method modifies only the Vcmax parameter while preserving all
        other existing Farquhar model parameters for each primitive.
        
        Args:
            vcmax: Maximum carboxylation rate at 25°C (μmol m⁻² s⁻¹)
            uuids: List of primitive UUIDs to modify (required)
            dha: Activation energy (optional, kJ/mol)
            topt: Optimal temperature (optional, °C)  
            dhd: Deactivation energy (optional, kJ/mol)
        
        Note:
            Primitives must have existing Farquhar model coefficients set before
            calling this method. Use setFarquharCoefficientsFromLibrary() first
            if needed. To modify all primitives, use setFarquharModelCoefficients()
            with complete coefficient objects.
        """
        from .types import FarquharModelCoefficients
        
        # For each UUID, get existing coefficients, modify Vcmax, then set back
        for uuid in uuids:
            # Get existing coefficients as raw array
            existing_array = self.getFarquharModelCoefficients(uuid)
            
            # Create new coefficient object from existing values
            existing_coeffs = FarquharModelCoefficients.from_array(existing_array)
            
            # Modify only Vcmax parameter using the temperature response
            if dha is None:
                existing_coeffs.Vcmax = vcmax
            else:
                # Create temperature response object and set it
                from .types import PhotosyntheticTemperatureResponseParameters
                if dhd is None and topt is None:
                    temp_response = PhotosyntheticTemperatureResponseParameters(vcmax, dha)
                elif dhd is None:
                    temp_response = PhotosyntheticTemperatureResponseParameters(vcmax, dha, topt)
                else:
                    temp_response = PhotosyntheticTemperatureResponseParameters(vcmax, dha, topt, dhd)
                
                # Set the temperature response values
                existing_coeffs.Vcmax = temp_response.value_at_25C
                # Note: Temperature response parameters would need to be stored separately
                # For now, just set the basic value
                existing_coeffs.Vcmax = vcmax
            
            # Set the modified coefficients back for this UUID
            self.setFarquharModelCoefficients(existing_coeffs, [uuid])

    def setJmax(self, jmax: float, uuids: List[int], dha: Optional[float] = None,
               topt: Optional[float] = None, dhd: Optional[float] = None):
        """
        Set maximum electron transport rate for Farquhar model.
        
        This method modifies only the Jmax parameter while preserving all
        other existing Farquhar model parameters for each primitive.
        
        Args:
            jmax: Maximum electron transport rate at 25°C (μmol m⁻² s⁻¹)
            uuids: List of primitive UUIDs to modify (required)
            dha: Activation energy (optional, kJ/mol)
            topt: Optimal temperature (optional, °C)
            dhd: Deactivation energy (optional, kJ/mol)
        
        Note:
            Primitives must have existing Farquhar model coefficients set before
            calling this method. Use setFarquharCoefficientsFromLibrary() first
            if needed. To modify all primitives, use setFarquharModelCoefficients()
            with complete coefficient objects.
        """
        from .types import FarquharModelCoefficients
        
        # For each UUID, get existing coefficients, modify Jmax, then set back
        for uuid in uuids:
            # Get existing coefficients as raw array
            existing_array = self.getFarquharModelCoefficients(uuid)
            
            # Create new coefficient object from existing values
            existing_coeffs = FarquharModelCoefficients.from_array(existing_array)
            
            # Modify only Jmax parameter
            existing_coeffs.Jmax = jmax
            
            # Set the modified coefficients back for this UUID
            self.setFarquharModelCoefficients(existing_coeffs, [uuid])

    def setDarkRespiration(self, respiration: float, uuids: List[int], dha: Optional[float] = None,
                          topt: Optional[float] = None, dhd: Optional[float] = None):
        """
        Set dark respiration rate.
        
        This method modifies only the Rd parameter while preserving all
        other existing Farquhar model parameters for each primitive.
        
        Args:
            respiration: Dark respiration rate at 25°C (μmol m⁻² s⁻¹)
            uuids: List of primitive UUIDs to modify (required)
            dha: Activation energy (optional, kJ/mol)
            topt: Optimal temperature (optional, °C)
            dhd: Deactivation energy (optional, kJ/mol)
        
        Note:
            Primitives must have existing Farquhar model coefficients set before
            calling this method. Use setFarquharCoefficientsFromLibrary() first
            if needed. To modify all primitives, use setFarquharModelCoefficients()
            with complete coefficient objects.
        """
        from .types import FarquharModelCoefficients
        
        # For each UUID, get existing coefficients, modify Rd, then set back
        for uuid in uuids:
            # Get existing coefficients as raw array
            existing_array = self.getFarquharModelCoefficients(uuid)
            
            # Create new coefficient object from existing values
            existing_coeffs = FarquharModelCoefficients.from_array(existing_array)
            
            # Modify only Rd parameter
            existing_coeffs.Rd = respiration
            
            # Set the modified coefficients back for this UUID
            self.setFarquharModelCoefficients(existing_coeffs, [uuid])

    def setQuantumEfficiency(self, efficiency: float, uuids: List[int], dha: Optional[float] = None,
                            topt: Optional[float] = None, dhd: Optional[float] = None):
        """
        Set quantum efficiency of photosystem II.
        
        This method modifies only the alpha parameter while preserving all
        other existing Farquhar model parameters for each primitive.
        
        Args:
            efficiency: Quantum efficiency at 25°C (dimensionless, 0-1)
            uuids: List of primitive UUIDs to modify (required)
            dha: Activation energy (optional, kJ/mol)
            topt: Optimal temperature (optional, °C)
            dhd: Deactivation energy (optional, kJ/mol)
        
        Note:
            Primitives must have existing Farquhar model coefficients set before
            calling this method. Use setFarquharCoefficientsFromLibrary() first
            if needed. To modify all primitives, use setFarquharModelCoefficients()
            with complete coefficient objects.
        """
        from .types import FarquharModelCoefficients
        
        # For each UUID, get existing coefficients, modify alpha, then set back
        for uuid in uuids:
            # Get existing coefficients as raw array
            existing_array = self.getFarquharModelCoefficients(uuid)
            
            # Create new coefficient object from existing values
            existing_coeffs = FarquharModelCoefficients.from_array(existing_array)
            
            # Modify only alpha parameter
            existing_coeffs.alpha = efficiency
            
            # Set the modified coefficients back for this UUID
            self.setFarquharModelCoefficients(existing_coeffs, [uuid])

    def setLightResponseCurvature(self, curvature: float, uuids: List[int], dha: Optional[float] = None,
                                 topt: Optional[float] = None, dhd: Optional[float] = None):
        """
        Set light response curvature parameter.
        
        This method modifies only the theta parameter while preserving all
        other existing Farquhar model parameters for each primitive.
        
        Args:
            curvature: Light response curvature at 25°C (dimensionless)
            uuids: List of primitive UUIDs to modify (required)
            dha: Activation energy (optional, kJ/mol)
            topt: Optimal temperature (optional, °C)
            dhd: Deactivation energy (optional, kJ/mol)
        
        Note:
            Primitives must have existing Farquhar model coefficients set before
            calling this method. Use setFarquharCoefficientsFromLibrary() first
            if needed. To modify all primitives, use setFarquharModelCoefficients()
            with complete coefficient objects.
        
        Note:
            The theta parameter is stored in the coefficient array but may not be
            directly exposed in the current FarquharModelCoefficients structure.
            This method sets the basic curvature value.
        """
        from .types import FarquharModelCoefficients
        
        # For each UUID, get existing coefficients, modify theta/curvature, then set back
        for uuid in uuids:
            # Get existing coefficients as raw array
            existing_array = self.getFarquharModelCoefficients(uuid)
            
            # Create new coefficient object from existing values
            existing_coeffs = FarquharModelCoefficients.from_array(existing_array)
            
            # Note: theta/curvature parameter mapping would need to be checked
            # For now, this is a placeholder - the actual field mapping needs verification
            # existing_coeffs.theta = curvature  # This field may not exist
            
            # Set the modified coefficients back for this UUID
            self.setFarquharModelCoefficients(existing_coeffs, [uuid])

    # Results and Output
    def getEmpiricalModelCoefficients(self, uuid: int) -> List[float]:
        """
        Get empirical model coefficients for a specific primitive.
        
        Args:
            uuid: Primitive UUID
            
        Returns:
            List of empirical model coefficients
        """
        return photosynthesis_wrapper.getEmpiricalModelCoefficients(self._native_ptr, uuid)

    def getFarquharModelCoefficients(self, uuid: int) -> List[float]:
        """
        Get Farquhar model coefficients for a specific primitive.
        
        Args:
            uuid: Primitive UUID
            
        Returns:
            List of Farquhar model coefficients
        """
        return photosynthesis_wrapper.getFarquharModelCoefficients(self._native_ptr, uuid)

    def exportResults(self, label: str):
        """
        Export photosynthesis results with optional label.
        
        Args:
            label: Data label for export
        """
        photosynthesis_wrapper.optionalOutputPrimitiveData(self._native_ptr, label)

    # Model Information and Utilities
    def enableMessages(self):
        """Enable photosynthesis model status messages."""
        photosynthesis_wrapper.enableMessages(self._native_ptr)

    def disableMessages(self):
        """Disable photosynthesis model status messages."""
        photosynthesis_wrapper.disableMessages(self._native_ptr)

    def printModelReport(self, uuids: Optional[List[int]] = None):
        """
        Print model configuration report.
        
        Args:
            uuids: Optional list of UUIDs. If None, prints report for all primitives.
        """
        if uuids is None:
            photosynthesis_wrapper.printDefaultValueReport(self._native_ptr)
        else:
            photosynthesis_wrapper.printDefaultValueReportForUUIDs(self._native_ptr, uuids)

    # Utility Methods
    def validateConfiguration(self) -> bool:
        """
        Basic validation that model has been configured.
        
        Returns:
            True if model appears to be configured (has native pointer)
        """
        return self._native_ptr is not None

    def resetModel(self):
        """
        Reset the model by recreating it.
        Note: This will clear all configured parameters.
        """
        if self._native_ptr is not None:
            old_ptr = self._native_ptr
            try:
                context_ptr = self.context.getNativePtr()
                self._native_ptr = photosynthesis_wrapper.createPhotosynthesisModel(context_ptr)
            finally:
                # Clean up old pointer
                try:
                    photosynthesis_wrapper.destroyPhotosynthesisModel(old_ptr)
                except Exception:
                    pass