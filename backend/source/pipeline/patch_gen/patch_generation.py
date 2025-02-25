import os
import re
import logging
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatchGeneration:
    def __init__(self, model: Any, file_contents: str, patterns: List[str], language: str) -> None:
        logger.info("Initializing PatchGeneration")
        self.model = model
        self.patterns = patterns
        self.file_contents = file_contents
        self.patch_candidates_dir = "patch_candidates"
        self.language = language
        self.patches = []
        logger.debug(f"Initialized with {len(patterns)} patterns for language: {language}")
    
    def get_prompt(self, pattern: str, current_code: str = "") -> str:
        logger.debug("Generating prompt" + (" with current code" if current_code else " without current code"))
        if current_code:
            return f"""Apply the given pattern fix to the current code while preserving previous fixes.  
            FOLLOW THE OUTPUT GUIDELINES COMPLETELY AND ALWAYS. ENSURE THAT THE CODE BLOCK IS FORMATTED AS SPECIFIED AND ALWAYS COMPLETED.

            Instructions:  
            - Integrate only the necessary modifications from the pattern into the current code.  
            - Maintain the structure and formatting of the original file.  
            - Return the full, updated file with all fixes applied.  
            - Do not add explanations, comments, or extra formatting.  

            Inputs:  
            - Current code state:  
            {current_code}  

            - Pattern to address:  
            {pattern} 

            Output:
            - The full, updated file with the vulnerability fixed.

            Format (ALWAYS FOLLOW THIS FORMAT):
            ```{self.language}
            // Provide the detailed code implementation here
            ```
            """
        else:
            return f"""
            Apply the provided pattern fix to the given file contents and return the entire updated file with the fixes applied.
            FOLLOW THE OUTPUT GUIDELINES COMPLETELY AND ALWAYS. ENSURE THAT THE CODE BLOCK IS FORMATTED AS SPECIFIED AND ALWAYS COMPLETED.

            Instructions:
            - Integrate only the relevant code modifications from the pattern fix into the file contents.
            - Maintain the structure and formatting of the original file.
            - Return the full, corrected file—do not output only the changes.
            - Do not add explanations, comments, or any extra formatting.

            Inputs:
            - file_contents: {self.file_contents}
            - pattern_fix: {pattern}

            Output:
            - The full, updated file with the vulnerability fixed.

            Format:
            ```{self.language}
            // Provide the detailed code implementation here
            ```
            """
        
    def return_code_block(self, text: str) -> str:
        logger.debug("Extracting code block from response")
        # regex pattern to match text between triple backticks
        pattern = r"```(?:[a-zA-Z]*)?\r?\n([\s\S]*?)```"

        # find first match and return only the code content
        match = re.search(pattern, text)
        if match:
            logger.debug("Successfully extracted code block")
            return match.group(1)
        else:
            logger.warning("No code block found in response")
            return ""

    def create_patch_files(self) -> None:
        logger.info("Starting patch file creation")

        current_code = self.file_contents

        # Iterate through the patterns and update the patch file
        logger.info(f"Processing {len(self.patterns)} patterns")
        for idx, pattern in enumerate(self.patterns):
            try:
                logger.info(f"Processing pattern {idx + 1}/{len(self.patterns)}")
                # Include current code state in the prompt
                prompt = self.get_prompt(pattern, current_code)
                logger.debug("Generated prompt, requesting model response")
                response = self.model.generate_response(prompt)

                # Update the current code with the new response
                current_code = self.return_code_block(response)
                self.patches.append(current_code)
                logger.info(f"Completed iteration {idx + 1}/{len(self.patterns)} - Updated Previous Patch")

            except Exception as e:
                logger.error(f"Error in iteration {idx + 1}: {str(e)}")
                continue

        logger.info(f"Completed all {len(self.patterns)} iterations. Final patch generated")
