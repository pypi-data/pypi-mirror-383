from abc import ABC, abstractmethod
import datetime

import malac.hd.build


__version__ = "1.2.0"

def version():
    if getattr(malac.hd.build, "EXTERNAL_BUILD", None):
        return __version__
    elif hasattr(malac.hd.build, "INTERNAL_BUILD_LABEL"):
        return f"{__version__}+{getattr(malac.hd.build, 'INTERNAL_BUILD_LABEL')}"
    else:
        return f"{__version__}+{datetime.date.today().strftime('%Y%m%d')}-dev"


class ConvertMaster(ABC):
    @abstractmethod
    def convert(self, input, o_module): # TODO:sbe adapt - this is not what is implemented/needed in base classes
        pass
        # return mapping_as_py

# not sure if this class will be needed, it is only unsed inside the into py converted map


class TransformMaster(ABC):
    @abstractmethod
    def transform(self, source_path, target_path):
        pass

# These are the mappings that might be used to generate code
list_m_modules = {
    ".4.fhir.xml": "fhir.r4.generator.structuremap",
    ".4.fhir.json": "fhir.r4.generator.structuremap",
    ".5.fhir.xml": "fhir.r5.generator.structuremap",
    ".5.fhir.json": "fhir.r5.generator.structuremap",
    ".fhir.xml": "fhir.r5.generator.structuremap",
    ".fhir.json": "fhir.r5.generator.structuremap",
    ".xml": "fhir.r5.generator.structuremap",
    ".json": "fhir.r5.generator.structuremap",
    ".4.map": "fhir.r4.generator.fml",
    ".4.fml": "fhir.r4.generator.fml",
    ".5.map": "fhir.r5.generator.fml",
    ".5.fml": "fhir.r5.generator.fml",
    ".map": "fhir.r5.generator.fml",
    ".fml": "fhir.r5.generator.fml"
}

# These are the models that might be used as source/target of a mapping
list_i_o_modules = dict()

import malac.models.fhir
list_i_o_modules.update(malac.models.fhir.list_i_o_modules)

i_o_modules_optional = ["malac.models.cda"]
for module_name in i_o_modules_optional:
    try:
        module_split = module_name.split(".")
        mod = getattr(__import__(".".join(module_split[:-1]), fromlist=[module_split[-1]]), module_split[-1])
        list_i_o_modules.update(mod.list_i_o_modules)
    except:
        pass
