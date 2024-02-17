import re
import json
from http import HTTPStatus
import dashscope
from typing import Tuple, List  
from termcolor import colored
from dotenv import load_dotenv
import os

# load_dotenv("../.env1")

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

class Qwen:
    def __init__(self, language: str = "en"):
        self.language = language
        dashscope.api_key = DASHSCOPE_API_KEY
    
    def generate_response(self, prompt: str, ai_model: str) -> str:
        """
        Generate a script for a video, depending on the subject of the video.

        Args:
            video_subject (str): The subject of the video.
            ai_model (str): The AI model to use for generation.


        Returns:

            str: The response from the AI model.

        """
        messages = [{"role": "user", "content": prompt}]
        if ai_model == 'qwen-turbo':
            response = dashscope.Generation.call(
                dashscope.Generation.Models.qwen_turbo,
                messages=messages,
                result_format="message",
            )
        elif ai_model == 'qwen-max':
            response = dashscope.Generation.call(
                dashscope.Generation.Models.qwen_max,
                messages=messages,
                result_format="message",
            )
        else:
            raise ValueError("Invalid AI model selected.")
        
        if response.status_code != HTTPStatus.OK:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return None
        return response.output.choices[0]['message']['content']
    
    def generate_script(self, video_subject: str, paragraph_number: int, ai_model: str) -> str:
        """
        Generate a script for a video, depending on the subject of the video, the number of paragraphs, and the AI model.

        Args:
            video_subject (str): The subject of the video.
            paragraph_number (int): The number of paragraphs to generate.
            ai_model (str): The AI model to use for generation.

        Returns:
            str: The response from the AI model.
        """

        # Build prompt
        if self.language == "en":
            prompt_en = f"""
            Generate a script for a video, depending on the subject of the video.
            Subject: {video_subject}
            Number of paragraphs: {paragraph_number}


            The script is to be returned as a string with the specified number of paragraphs.

            Here is an example of a string:
            "This is an example string."

            Do not under any circumstance reference this prompt in your response.

            Get straight to the point, don't start with unnecessary things like, "welcome to this video".

            Obviously, the script should be related to the subject of the video.

            YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
            ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT.
            """
        else:
            prompt_zh = f"""
            根据视频的主题生成视频脚本。
            主题：{video_subject}
            段落数：{paragraph_number}

            该脚本将以具有指定段落数的字符串形式返回。
            示例如下：
                主题：如何通过冥想治疗失眠
                段落数：2
                在我们忙碌的生活中，失眠常常成为一种困扰。然而，科学已证实，冥想作为一种古老的自我疗愈方式，能有效地帮助改善睡眠质量。让我们一起探索如何通过日常冥想实践来战胜失眠的困扰。
                首先，找一个安静且舒适的空间，确保手机或其他电子设备处于静音模式。闭上眼睛，深深地呼吸几次，感受气息在鼻腔和腹部之间的流动。接着，将注意力集中在你的呼吸上，每当思绪飘忽时，轻轻地把它们引导回当下，回到自然的呼吸节奏。接下来，尝试进行4-5分钟的身体扫描冥想，从脚底开始，逐渐向上扫过腿部、躯干、手臂和头部，关注并接纳每一个部位的感觉，无需判断或改变。这样做有助于放松身心，减少压力和焦虑，从而为优质的睡眠铺平道路。每天坚持10-20分钟的冥想练习，你会发现自己的睡眠质量有了显著提升。记住，关键在于持之以恒，让冥想成为改善失眠问题的有效工具。现在，就让我们带着内心的平静和对更好睡眠的期待，步入这个宁静的内在世界吧）
            
            在任何情况下都不要在回复中引用此提示。
            直奔主题，不要以“欢迎观看本视频”之类的不必要的内容开头。
            脚本应与视频的主题相关。
            你绝对不能在脚本中包含任何类型的标记或格式，绝对不能使用标题，只需要纯文本。
            只返回脚本的原始内容。不要在脚本中包含“旁白”、“解说”或类似的指示语，不要使用括号来讲解背景。你绝对不能提到提示，或者脚本本身的任何内容。也不要谈论段落数或行数。
            你只需要写脚本文本，其它的一概不需要。
            """

        # Generate script
        if self.language == "en":
            response = self.generate_response(prompt_en, ai_model)
        else:
            response = self.generate_response(prompt_zh, ai_model)
        
        print(colored(response, "cyan"))

        # Return the generated script
        if response:
            # Clean the script
            # Remove asterisks, hashes
            response = response.replace("*", "")
            response = response.replace("#", "")

            #Remove markdown syntax
            response = re.sub(r"\[.*\]", "", response)
            response = re.sub(r"\(.*\)", "", response)

            # Split the script into paragraphs
            paragraphs = response.split("\n\n")

            # Select the specified number of paragraphs
            selected_paragraphs = paragraphs[:paragraph_number]

            # Join the selected paragraphs into a single string
            final_script = "\n\n".join(selected_paragraphs)

            print(colored(f"Number of paragraphs used: {len(selected_paragraphs)}", "green"))
            return final_script
        else:
            print(colored("[-] QWen returned an empty response.", "red"))
            return None
    
    def get_search_terms(self, video_subject: str, amount: int, script: str, ai_model: str) -> List[str]:
        '''
        Generate a JSON-Array of search terms for stock videos,
        depending on the subject of a video.

        Args:
            video_subject (str): The subject of the video.
            amount (int): The amount of search terms to generate.
            script (str): The script of the video.
            ai_model (str): The AI model to use for generation.

        Returns:
            List[str]: The search terms for the video subject.
        '''

        # Build prompt
        # if self.language == "en":
        
        prompt_en = f"""
        Generate {amount} search terms for stock videos,
        depending on the subject of a video.
        Subject: {video_subject}

        The search terms are to be returned as a JSON-Array of strings.
        
        Each search term should consist of 1-3 words,
        always add the main subject of the video.
        
        YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
        YOU MUST NOT RETURN ANYTHING ELSE. 
        YOU MUST NOT RETURN THE SCRIPT.
        
        The search terms must be related to the subject of the video.
        Here is an example of a JSON-Array of strings:
        ["search term 1", "search term 2", "search term 3"]

        For context, here is the full text:
        {script}
        return english content!!!
        """
        # else:
            # prompt_zh = f"""
            # 生成{amount}个与视频主题相关的库存视频搜索词。
            # 主题：{video_subject}

            # 应将搜索词作为字符串的JSON-Array返回。
            # 每个搜索词应由1-3个单词组成，
            # 并始终包含视频的主要主题。

            # 你只能返回JSON-Array的字符串。
            # 你不能返回其他任何东西。
            # 你不能返回脚本。

            # 搜索词必须与视频的主题相关。
            # 这是一个JSON-Array字符串的示例：
            # ["搜索词1", "搜索词2", "搜索词3"]

            # 以下是完整文本：
            # {script}
            # """
        
        # if self.language == "en":
        response = self.generate_response(prompt_en, ai_model)
        # response = self.generate_response("将中文翻译成英文，不要改变任何格式"+response_original, ai_model)
        # else:
            # response = self.generate_response(prompt_zh, ai_model)

        search_terms = []
        try:
            search_terms = json.loads(response)
            if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
                raise ValueError("Response is not a list of strings.")
        except (json.JSONDecodeError, ValueError):
            print(colored("[*] QWen returned an unformatted response. Attempting to clean...", "yellow"))
            match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
            if match:
                try:
                    search_terms = json.loads(match.group())
                except json.JSONDecodeError:
                    print(colored("[-] Could not parse response.", "red"))
                    return []
        # Let user know
        print(colored(f"\nGenerated {len(search_terms)} search terms: {', '.join(search_terms)}", "cyan"))

        return search_terms
    
    def generate_metadata(self, video_subject: str, script: str, ai_model: str) -> Tuple[str, str, List[str]]:  
        """  
        Generate metadata for a YouTube video, including the title, description, and keywords.  
    
        Args:  
            video_subject (str): The subject of the video.  
            script (str): The script of the video.  
            ai_model (str): The AI model to use for generation.  
    
        Returns:  
            Tuple[str, str, List[str]]: The title, description, and keywords for the video.  
        """  
    
        # Build prompt for title
        if self.language == "en":
            title_prompt_en = f"""  
            Generate a catchy and SEO-friendly title for a YouTube shorts video about {video_subject}.  
            """  
        else:
            title_prompt_zh = f"""  
            为关于{video_subject}的YouTube短视频生成一个引人注目且符合SEO的标题。  
            """
        
        # Generate title
        if self.language == "en":
            title = self.generate_response(title_prompt_en, ai_model).strip()
        else:
            title = self.generate_response(title_prompt_zh, ai_model).strip()  
        
        # Build prompt for description
        if self.language == "en":
            description_prompt_en = f"""  
            Write a brief and engaging description for a YouTube shorts video about {video_subject}.  
            The video is based on the following script:  
            {script}  
            """  
        else:
            description_prompt_zh = f"""  
            为关于{video_subject}的YouTube短视频编写简洁而引人入胜的描述。  
            该视频基于以下脚本：  
            {script}  
            """ 
    
        # Generate description  
        if self.language == "en":
            description = self.generate_response(description_prompt_en, ai_model).strip()
        else:
            description = self.generate_response(description_prompt_zh, ai_model).strip()
    
        # Generate keywords  
        keywords = self.get_search_terms(video_subject, 6, script, ai_model)  

        return title, description, keywords