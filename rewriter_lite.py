import logging
from anthropic import Anthropic
import os
import re

class ContentProcessor:
    def __init__(self, guidelines_file: str, api_key: str, input_dir: str, output_dir: str):
        """
        Initialize the content processor.
        
        Args:
            guidelines_file (str): Path to the file containing content guidelines
            api_key (str): Anthropic API key for Claude access
            input_dir (str): Directory containing input markdown files
            output_dir (str): Directory to save output files
        """
        self.guidelines = self._load_guidelines(guidelines_file)
        self.anthropic = Anthropic(api_key=api_key)
        self.logger = self._setup_logger()
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

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

    def sanitize_filename(self, filename: str) -> str:
        """
        Convert a filename to a safe filename by removing or replacing 
        characters that are not allowed in filenames.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename with .md extension
        """
        # Remove or replace characters not allowed in filenames
        sanitized = re.sub(r'[^\w\-\s]', '', filename)
        
        # Replace multiple spaces or hyphens with a single underscore
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        
        # Trim leading/trailing whitespace and underscores
        sanitized = sanitized.strip('_')
        
        # Truncate to a reasonable length
        sanitized = sanitized[:250]
        
        # Ensure we have a non-empty filename
        if not sanitized:
            sanitized = 'untitled'
        
        # Add .md extension
        return f"{sanitized}.md"

    def extract_generated_title(self, content: str) -> str:
        """
        Extract the title that Claude generated from the markdown content.
        
        Args:
            content (str): Processed markdown content
            
        Returns:
            str: Generated title, or None if not found
        """
        try:
            lines = content.split('\n')
            found_core_section = False
            
            for line in lines:
                if '# Core Identification' in line:
                    found_core_section = True
                    continue
                    
                if found_core_section and line.startswith('Title:'):
                    title = line.replace('Title:', '', 1).strip()
                    self.logger.info(f"Found LLM-generated title: {title}")
                    return title
                    
                if found_core_section and line.startswith('#'):
                    break
            
            self.logger.warning("Could not find LLM-generated title in Core Identification section")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting generated title: {str(e)}")
            return None

    def rewrite_content(self, content: str, original_filename: str) -> str:
        """Use Claude to rewrite the content according to guidelines."""
        try:
            prompt = f"""Please rewrite the following content according to these guidelines:

{self.guidelines}

Here is the content to rewrite:

{content}

Your response MUST follow this exact format:

# Core Identification
Title: [Your chosen title for this content]
Source: {original_filename}
[Rest of the rewritten content with appropriate headers and formatting]

The title you choose in the Core Identification section will be used as the document's filename, so please ensure it is clear and descriptive. Do not omit or modify the "Title:" prefix in the Core Identification section."""

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
            
            return message.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error rewriting content with Claude: {str(e)}")
            return f"# Core Identification\n\n{content}"

    def process_files(self):
        """
        Main method to process markdown files from input directory and save to output directory.
        """
        try:
            # Get list of markdown files
            markdown_files = [f for f in os.listdir(self.input_dir) 
                            if f.endswith(('.md', '.markdown'))]
            
            processed_count = 0
            
            self.logger.info(f"Starting to process {len(markdown_files)} markdown files")
            
            for filename in markdown_files:
                try:
                    self.logger.info(f"\nProcessing file: {filename}")
                    
                    # Read input file
                    input_path = os.path.join(self.input_dir, filename)
                    with open(input_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if not content:
                        self.logger.error(f"Empty file: {filename}")
                        continue
                        
                    self.logger.info(f"Read content length: {len(content)} characters")
                    self.logger.info("Sending content to Claude for rewriting...")
                    
                    # Rewrite content using Claude
                    processed_content = self.rewrite_content(content, filename)
                    
                    if not processed_content:
                        self.logger.error("No content returned from Claude")
                        continue
                        
                    self.logger.info("Content rewritten, extracting title...")
                    
                    # Extract the title that Claude generated
                    generated_title = self.extract_generated_title(processed_content)
                    if not generated_title:
                        self.logger.warning(f"No title found in Claude's output, using original filename")
                        generated_title = os.path.splitext(filename)[0]
                    
                    self.logger.info(f"Using title: {generated_title}")
                    
                    # Create filename from the generated title
                    new_filename = self.sanitize_filename(generated_title)
                    output_path = os.path.join(self.output_dir, new_filename)
                    
                    # Ensure unique filename
                    counter = 1
                    base_name = new_filename.rsplit('.', 1)[0]
                    while os.path.exists(output_path):
                        output_path = os.path.join(self.output_dir, f"{base_name}-{counter}.md")
                        counter += 1
                    
                    self.logger.info(f"Saving to file: {output_path}")
                    
                    # Save content to file
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(processed_content)
                    
                    processed_count += 1
                    self.logger.info(f"Successfully processed file {processed_count}")
                
                except Exception as e:
                    self.logger.error(f"Error processing file {filename}: {str(e)}")
                    self.logger.error("Full error: ", exc_info=True)
                    continue
                    
            self.logger.info(f"\nProcessing summary:")
            self.logger.info(f"Total files found: {len(markdown_files)}")
            self.logger.info(f"Successfully processed: {processed_count}")
            self.logger.info(f"Failed/skipped: {len(markdown_files) - processed_count}")
            
        except Exception as e:
            self.logger.error(f"Error in process_files: {str(e)}")
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
    """Example usage of the ContentProcessor class."""
    # Read API key from file
    api_key = read_api_key('api_key.txt')
    if not api_key:
        raise ValueError("API key file is empty")
    
    # Initialize processor with guidelines and API key
    processor = ContentProcessor(
        'guidelines.txt',
        api_key,
        'input',  # Input directory containing markdown files
        'output'  # Output directory for processed files
    )
    
    # Process files and save output
    processor.process_files()


if __name__ == "__main__":
    main()