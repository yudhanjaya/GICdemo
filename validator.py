import logging
from anthropic import Anthropic
import os
import re
import difflib
import time
from typing import Tuple, Optional

class ContentValidator:
    def __init__(self, guidelines_file: str, api_key: str, input_dir: str, validated_dir: str = "validatedoutputs", logs_dir: str = "validationlogs"):
        """
        Initialize the content validator.
        
        Args:
            guidelines_file (str): Path to the file containing content guidelines
            api_key (str): Anthropic API key for Claude access
            input_dir (str): Directory containing files to validate
            validated_dir (str): Directory where validated files will be saved
            logs_dir (str): Directory where validation logs will be saved
        """
        self.guidelines = self._load_guidelines(guidelines_file)
        self.anthropic = Anthropic(api_key=api_key)
        self.logger = self._setup_logger()
        self.input_dir = input_dir
        
        # Create validated outputs directory
        self.validated_dir = validated_dir
        os.makedirs(self.validated_dir, exist_ok=True)
        
        # Create logs directory
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Create dated log file
        current_date = time.strftime('%Y-%m-%d')
        self.diff_log_file = os.path.join(
            self.logs_dir,
            f"validation_diffs_{current_date}.log"
        )

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _load_guidelines(self, file_path: str) -> str:
        """Load content guidelines from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.logger.error(f"Error loading guidelines: {str(e)}")
            raise

    def validate_content(self, content: str) -> Tuple[bool, str]:
        """
        Use Claude to validate if content follows guidelines.
        
        Args:
            content (str): Content to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, explanation)
        """
        try:
            prompt = f"""Please validate if the following content follows these guidelines:

{self.guidelines}

Here is the content to validate:

{content}

Your response must follow this exact format:

VALID: [true/false]
EXPLANATION: [detailed explanation of why the content does or doesn't follow guidelines]
ISSUES: [if not valid, list specific issues that need to be fixed, each on a new line starting with - ]

Only respond with the above format, no other text."""

            message = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.0,
                system="You are a meticulous content validator. Be thorough and precise in your analysis.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response = message.content[0].text
            
            # Parse the response
            valid = False
            explanation = "Validation failed"
            
            for line in response.split('\n'):
                if line.startswith('VALID:'):
                    valid = line.replace('VALID:', '').strip().lower() == 'true'
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
            
            return valid, explanation
            
        except Exception as e:
            self.logger.error(f"Error validating content with Claude: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def rewrite_if_needed(self, content: str, original_filename: str) -> Optional[str]:
        """
        Validate content and rewrite if it doesn't follow guidelines.
        
        Args:
            content (str): Content to validate and potentially rewrite
            original_filename (str): Name of the original file
            
        Returns:
            Optional[str]: Rewritten content if needed, None if content is valid
        """
        try:
            # First validate the content
            is_valid, explanation = self.validate_content(content)
            
            if is_valid:
                self.logger.info("Content follows guidelines, no rewrite needed")
                return None
                
            self.logger.info(f"Content needs rewriting: {explanation}")
            
            # Rewrite the content
            prompt = f"""Please rewrite the following content to follow these guidelines:

{self.guidelines}

The content currently has these issues:
{explanation}

Here is the content to rewrite:

{content}

Your response MUST follow this exact format:

# Core Identification
Title: [preserve existing title from original content]
Source: {original_filename}
[Rest of the rewritten content with appropriate headers and formatting]

Please preserve the existing title from the Core Identification section."""

            message = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.3,
                system="You are a helpful, expert content editor. Follow the user's instructions as best as possible.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            rewritten = message.content[0].text
            
            # Validate the rewritten content
            rewritten_valid, rewritten_explanation = self.validate_content(rewritten)
            
            if not rewritten_valid:
                self.logger.error(f"Rewritten content still doesn't follow guidelines: {rewritten_explanation}")
                # Could potentially try rewriting again with stricter instructions
                return None
                
            return rewritten
            
        except Exception as e:
            self.logger.error(f"Error rewriting content: {str(e)}")
            return None

    def show_diff(self, original: str, rewritten: str):
        """Show the differences between original and rewritten content."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            rewritten.splitlines(keepends=True),
            fromfile='original',
            tofile='rewritten'
        )
        return ''.join(diff)

    def validate_files(self):
        """
        Main method to validate and rewrite files if needed.
        """
        try:
            # Get list of markdown files
            markdown_files = [f for f in os.listdir(self.input_dir) 
                            if f.endswith(('.md', '.markdown'))]
            
            self.logger.info(f"Starting to validate {len(markdown_files)} markdown files")
            
            files_checked = 0
            files_rewritten = 0
            files_failed = 0
            
            for filename in markdown_files:
                try:
                    self.logger.info(f"\nValidating file: {filename}")
                    
                    # Read file content
                    input_path = os.path.join(self.input_dir, filename)
                    with open(input_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if not content:
                        self.logger.error(f"Empty file: {filename}")
                        files_failed += 1
                        continue
                    
                    # Validate and rewrite if needed
                    rewritten = self.rewrite_if_needed(content, filename)
                    
                    # Path for the validated output
                    validated_path = os.path.join(self.validated_dir, filename)
                    
                    if rewritten is None:
                        self.logger.info(f"File {filename} is valid")
                        # Copy valid file to validated outputs
                        with open(validated_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        files_checked += 1
                        continue
                    
                    # Show diff and save to log file
                    diff = self.show_diff(content, rewritten)
                    self.logger.info(f"Changes made:\n{diff}")
                    
                    # Save diff to file
                    with open(self.diff_log_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n{'='*80}\n")
                        f.write(f"File: {filename}\n")
                        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"{'='*80}\n")
                        f.write(diff)
                        f.write("\n")
                    
                    # Write rewritten content to validated outputs
                    with open(validated_path, 'w', encoding='utf-8') as f:
                        f.write(rewritten)
                    
                    self.logger.info(f"Rewrote file {filename} to {validated_path}")
                    files_rewritten += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing file {filename}: {str(e)}")
                    files_failed += 1
                    continue
            
            self.logger.info(f"\nValidation summary:")
            self.logger.info(f"Total files: {len(markdown_files)}")
            self.logger.info(f"Valid files (no rewrite needed): {files_checked}")
            self.logger.info(f"Files rewritten: {files_rewritten}")
            self.logger.info(f"Files failed: {files_failed}")
            self.logger.info(f"All validated files saved to: {self.validated_dir}")
            
        except Exception as e:
            self.logger.error(f"Error in validate_files: {str(e)}")
            self.logger.error("Full error: ", exc_info=True)
            raise


def read_api_key(key_file: str) -> str:
    """Read API key from a file."""
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Error reading API key from {key_file}: {str(e)}")


def main():
  
    # Read API key from file
    api_key = read_api_key('api_key.txt')
    if not api_key:
        raise ValueError("API key file is empty")
    
    # Initialize validator with guidelines and API key
    validator = ContentValidator(
        'guidelines.txt',
        api_key,
        'output',  # Directory containing input files to validate
        'validatedoutputs',  # Directory for validated files
        'validationlogs'  # Directory for validation logs
    )
    
    # Validate files and save to validatedoutputs
    validator.validate_files()


if __name__ == "__main__":
    main()