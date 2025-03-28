# AIDA AI Handler module
# Manages interactions with Azure AI services for code translation

"""
*****************************************************************************************************************************************************************
This video is the reason I use Azure for API calls:  https://www.youtube.com/watch?v=YP8mV_2RDLc

I used azure because with github personal token deepseekv3 model you have 50 prompts per day and there is also openai-4o model as a free model but I didn't want
to add them because when making api calls it uses Azure again as import

https://github.com/marketplace?type=models
https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits

*****************************************************************************************************************************************************************
"""

from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient

class AIHandler:
    """
    Handles AI processing for the AIDA plugin.
    Manages communication with Azure AI models to translate decompiled pseudocode.
    """
    def __init__(self) -> None:
        """
        Initialize the AI Handler with the system prompt used for code translation.
        The system prompt instructs the AI how to process the decompiled pseudocode.
        """
        self.__SYSTEM_PROMPT: str = '''
            Act as an expert reverse engineer and code translator. Your task is to convert IDA Pro decompiled pseudocode into clean, modern, readable [language_combobox_value] code.
            
            Key requirements:
            1. You will receive pseudocode with MULTIPLE FUNCTIONS. The MAIN function is at the TOP, and HELPER functions are BELOW.
            2. You MUST identify each "sub_XXXXXX" call in the main function and REPLACE them with appropriate calls to your translated helper functions.
            3. Create meaningful names for the helper functions based on their behavior.
            4. Your final code MUST contain implementations for ALL helper functions AND properly CALL them from the main function.
            5. Improve readability by using descriptive names and modern syntax.
            6. Replace low-level pointer operations with safer alternatives appropriate for [language_combobox_value].
            
            CRITICAL:
            - When you see a call like "sub_18000F2C0(lpSubKey, Name)" in the main function, you MUST implement the corresponding helper function AND call it with the right parameters.
            - DO NOT reimplement logic in the main function that should be in helper functions.
            - ENSURE all helper functions are properly connected to the main function.
            
            Example:
            If the main function calls "sub_1234(a, b)" and below you see "void sub_1234(int* a, char* b)", you must:
            1. Create a proper implementatio
                    print(pseudocode) (e.g., "void processData(int* value, char* text)")
            2. Call it appropriately in the main function (e.g., "processData(a, b)")
            
            Your output must be ONLY the translated code with no markdown, explanations, or comments around it.
        '''

    async def process_request(self, model_name: str, pseudocode: str, target_language: str, api_key: str) -> str:
        """
        Process the user's code translation request by routing to the appropriate AI model.
        
        Args:
            model_name: Name of the AI model to use for translation
            pseudocode: IDA Pro decompiled pseudocode to translate
            target_language: Target programming language for translation
            api_key: API key for Azure AI services
            
        Returns:
            Translated code as a string or error message
        """
        try:
            # Replace the language placeholder in the system prompt
            system_prompt: str = self.__SYSTEM_PROMPT.replace("[language_combobox_value]", target_language)

            # Route request to the appropriate model handler
            if model_name.lower().startswith("deepseek"):
                return await self.__process_deepseek(model_name, system_prompt, pseudocode, api_key, target_language)

        except Exception as e:
            return f"Error processing request: {str(e)}"

    async def __process_deepseek(self, model: str, system_prompt: str, pseudocode: str, api_key: str, target_language: str) -> str:
        """
        Process the request using the DeepSeek model on Azure AI.
        
        Args:
            model: Complete model name
            system_prompt: System instructions for the AI model
            pseudocode: IDA Pro decompiled pseudocode to translate
            api_key: API key for Azure AI services
            target_language: Target programming language for translation
            
        Returns:
            Translated code as a string
        """
        # Initialize the client with Azure AI endpoint and credentials
        client: ChatCompletionsClient = ChatCompletionsClient(
            endpoint="https://models.inference.ai.azure.com",
            credential=AzureKeyCredential(api_key),
        )

        # Send the completion request to the AI model
        response = client.complete(
            messages=[
                SystemMessage(f"{system_prompt}"),
                UserMessage(f"Translate this IDA Pro decompiled pseudocode to clean, modern {target_language} code. Return ONLY the translated code without any markdown formatting, explanations, or comments. Do NOT use code blocks with backticks. Just output the raw code directly:\n\n{pseudocode}"),
            ],
            model=model,
            temperature=0,  # Use deterministic output
            max_tokens=2048,  # Allow sufficient tokens for complex translations
            top_p=1  # Use highest probability tokens
        )

        # Return the content of the model's response
        return response.choices[0].message.content