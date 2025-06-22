from openai import OpenAI
import streamlit as st

import google.generativeai as genai

class TokenException(Exception):
        """Exception for handling invalid or expired tokens."""
pass

class OpenAIClientSingleton:
    _instance = None

    @classmethod
    def get_gpt4o_openai_client(cls):
        if cls._instance is None:
            api_key = st.secrets['gpt4o_openai_api_key']
            api_organization_id = st.secrets['org_id']
            cls._instance = OpenAI(api_key = api_key, organization= api_organization_id)
        return cls._instance

class GoogleGeminiClientSingleton:
     _instance = None

     @classmethod
     def initialise_gemini_client(cls):
          if cls._instance is None:
            api_key = st.secrets['google_api_key']
            genai.configure(api_key=api_key)
            cls._instance = genai.GenerativeModel('gemini-2.0-flash-exp')
          return cls._instance
     @classmethod
     def initialise_gemini_client_byok(cls,api_key):
          if cls._instance is None:
            genai.configure(api_key=api_key)
            cls._instance = genai.GenerativeModel('gemini-2.0-flash-exp')
          return cls._instance

class LlamaClientSingleton:
     _instance = None

     @classmethod
     def get_llama_openai_client(cls):
        # meta-llama/Llama-3.2-11B-Vision-Instruct
        if cls._instance is None:
            api_key = st.secrets['hf_api_key']
            api_base_url = "https://api-inference.huggingface.co/v1/"
            cls._instance = OpenAI(api_key = api_key, base_url= api_base_url)
        return cls._instance