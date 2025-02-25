import json
import sys
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

from backend.source.pipeline.rag.rag import RAG
from backend.source.pipeline.fault_loc.fault_localization import FaultLocalization
from backend.source.pipeline.pattern_match.pattern_matching import PatternMatch
from backend.source.pipeline.patch_gen.patch_generation import PatchGeneration
from backend.source.pipeline.patch_valid.patch_validation import PatchValidation

"""from rag.rag import RAG
from fault_loc.fault_localization import FaultLocalization
from pattern_match.pattern_matching import PatternMatch
from patch_gen.patch_generation import PatchGeneration
from patch_valid.patch_validation import PatchValidation"""

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from source.model.model import Model

# load api key from .env
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

"""
this pipeline will be the main process for the pipeline that is being integrated :)
"""
class Pipeline:
    def __init__(self, filename: str, precode_content: str, model: Optional[str] = None, test: bool = False) -> None:
        self.model: Optional[Model]
        self.rag: Optional[RAG]
        
        if test:
            self.set_model(test=True)
        else:
            self.set_model(model_selection=model, api_key=fireworks_api_key, provider="fireworks")
        self.set_rag()

        self.precode_content = precode_content
        self.filename = filename

        # start rag setup
        content = [{
            "filename": self.filename,
            "content": self.precode_content
        }]
        self.rag.embed_code(content)

        self.localization: Optional[str] = None
        self.patterns: Optional[List[str]] = [None]
        self.pre_patterns: Optional[List[str]] = [None]
        self.patches: Optional[str] = None
        self.validation: Optional[List[str]] = [None]

    def set_rag(self) -> None:
        self.rag = RAG()

    # define the model being used throughout the pipeline
    def set_model(self, model_selection: Optional[str] = None, api_key: Optional[str] = None, provider: Optional[str] = None, test: bool = False) -> None:
        try:
            self.model = Model(model_selection, api_key, provider, test)
        except Exception as e:
            print(f"Error setting model: {e}")

    # first stage which determines where the fault/vulnerability is
    def fault_localization(self):
        fl = FaultLocalization(self.model, self.precode_content)
        fl.calculate_fault_localization()
        self.localization = fl.get_fault_localization()

    # second stage determines the type of fault/vulnerability
    def pattern_matching(self):
        pm = PatternMatch(self.model, self.rag, self.localization)
        pm.execute_pattern_matching()
        self.patterns = pm.patterns
        self.pre_patterns = pm.pre_patterns

    # third stage creates the patches and places them in the code
    def patch_generation(self, output_dir: str = "patch_candidates") -> str:
        pg = PatchGeneration(self.model, self.precode_content, self.patterns, "java")
        pg.create_patch_files()
        self.patches = pg.patches

    # last stage determines if the fixes are corrected
    def patch_validation(self):
        validator = PatchValidation(self.model, self.patches[len(self.patches) - 1], faults=self.localization, language="java")
        self.validation = validator.validate_patches()

    def run_pipline(self) -> None:
        self.localization = None
        self.patterns = [None]
        self.patches = None
        self.validation = [None]
        # first stage
        self.fault_localization()
        # second stage
        self.pattern_matching()
        # third stage
        self.patch_generation()
        # fourth stage
        self.patch_validation()