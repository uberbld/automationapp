import os
from openai import OpenAI # Corrected import for OpenAI v1.x.x
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMHandler:
    def __init__(self, api_key=None, model_name="gpt-3.5-turbo"):
        if api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass it directly.")
        else:
            self.api_key = api_key

        self.model_name = model_name
        # Initialize the OpenAI client with the API key
        self.client = OpenAI(api_key=self.api_key) # Corrected client initialization

    def generate_cover_letter(self, job_title, job_description, user_profile):
        """Generates a personalized cover letter using an LLM."""
        prompt = f"""
        Generate a compelling and personalized cover letter for the following job opportunity.
        Ensure the tone is professional and enthusiastic.

        Job Title: {job_title}

        Job Description:
        {job_description}

        My Profile/Resume Highlights:
        {user_profile}

        Cover Letter:
        """
        try:
            response = self.client.chat.completions.create( # Corrected API call
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,  # Adjust as needed
                temperature=0.7  # Adjust for creativity vs. precision
            )
            # Correctly access the response content
            cover_letter = response.choices[0].message.content.strip()
            return cover_letter
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return None

    def customize_proposal(self, base_proposal, job_specifics):
        """Customizes a base proposal with job-specific details using an LLM."""
        prompt = f"""
        Customize the following base proposal to make it highly relevant for the job specifics provided.
        Incorporate the job specifics naturally into the proposal.

        Base Proposal:
        {base_proposal}

        Job Specifics:
        {job_specifics}

        Customized Proposal:
        """
        try:
            response = self.client.chat.completions.create( # Corrected API call
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that tailors job proposals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400, # Adjust as needed
                temperature=0.5
            )
            # Correctly access the response content
            customized_proposal = response.choices[0].message.content.strip()
            return customized_proposal
        except Exception as e:
            print(f"Error customizing proposal: {e}")
            return None

# Example Usage (Optional - for testing purposes)
if __name__ == '__main__':
    # Ensure you have a .env file with OPENAI_API_KEY or pass it directly for testing
    # For example, create a .env file in the same directory with:
    # OPENAI_API_KEY="your_actual_openai_api_key"

    print("Initializing LLMHandler...")
    try:
        llm = LLMHandler() # Assumes OPENAI_API_KEY is in .env
        print("LLMHandler initialized.")

        # Test cover letter generation
        print("\nTesting cover letter generation...")
        job_title_test = "Senior Software Engineer"
        job_desc_test = """
        We are looking for a Senior Software Engineer with 5+ years of experience in Python,
        cloud technologies (AWS/Azure), and a passion for building scalable systems.
        Experience with microservices and Kubernetes is a plus.
        """
        user_profile_test = """
        - 8 years of Python development expertise.
        - Proficient in AWS services (EC2, S3, Lambda).
        - Led a team to develop and deploy a microservices-based application.
        - Strong problem-solving skills and a collaborative mindset.
        """
        cover_letter = llm.generate_cover_letter(job_title_test, job_desc_test, user_profile_test)
        if cover_letter:
            print("\nGenerated Cover Letter:")
            print(cover_letter)
        else:
            print("\nCould not generate cover letter (check API key and OpenAI service status).")

        # Test proposal customization
        print("\nTesting proposal customization...")
        base_proposal_test = "I am a skilled developer with experience in web technologies and project management."
        job_specifics_test = "This project requires specific expertise in migrating a legacy PHP application to a modern Node.js stack, focusing on performance and security."

        custom_proposal = llm.customize_proposal(base_proposal_test, job_specifics_test)
        if custom_proposal:
            print("\nCustomized Proposal:")
            print(custom_proposal)
        else:
            print("\nCould not customize proposal.")

    except ValueError as ve:
        print(f"ValueError: {ve}")
        print("Please ensure your OPENAI_API_KEY is set correctly in a .env file or passed to the constructor.")
    except Exception as e:
        print(f"An unexpected error occurred during LLMHandler testing: {e}")

    print("\nLLMHandler test finished.")
