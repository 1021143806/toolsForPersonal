"""
硅基流动 API 客户端
"""

import http.client
import json
import logging

# 添加硅基API请求日志记录器
api_logger = logging.getLogger('siliconflow_api')
api_handler = logging.FileHandler('siliconflow_api_requests.log')
api_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
api_logger.addHandler(api_handler)
api_logger.setLevel(logging.INFO)


class SiliconFlowClient:
    """硅基流动 API 客户端"""
    
    def __init__(self, config):
        self.config = config
        self.siliconflow_token = config['siliconflow']['token']
        self.model = config['siliconflow']['model']
        self.api_settings = config['api_settings']
    
    def send_content(self, content):
        """发送内容到硅基流动API"""
        try:
            api_logger.info("开始发送请求到硅基API...")
            
            conn = http.client.HTTPSConnection("api.siliconflow.cn")
            
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "stream": False,
                "max_tokens": self.api_settings['max_tokens'],
                "enable_thinking": False,
                "thinking_budget": 4096,
                "min_p": 0.05,
                "stop": None,
                "temperature": self.api_settings['temperature'],
                "top_p": self.api_settings['top_p'],
                "top_k": self.api_settings['top_k'],
                "frequency_penalty": self.api_settings['frequency_penalty'],
                "n": 1,
                "response_format": {
                    "type": "text"
                }
            })
            
            headers = {
                'Authorization': self.siliconflow_token,
                'Content-Type': 'application/json'
            }
            
            # 记录请求详情
            api_logger.info(f"请求URL: https://api.siliconflow.cn/v1/chat/completions")
            api_logger.info(f"请求模型: {self.model}")
            api_logger.info(f"请求参数: max_tokens={self.api_settings['max_tokens']}, temperature={self.api_settings['temperature']}")
            api_logger.info(f"请求内容长度: {len(content)} 字符")
            api_logger.info(f"完整请求载荷: {payload}")
            
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            data = res.read()
            response_text = data.decode("utf-8")
            
            api_logger.info(f"HTTP状态码: {res.status}")
            api_logger.info(f"响应头: {dict(res.getheaders())}")
            api_logger.info(f"响应内容长度: {len(response_text)} 字符")
            
            if res.status == 200:
                response_json = json.loads(response_text)
                
                # 详细记录响应信息
                api_logger.info("API调用成功")
                api_logger.info(f"完整响应JSON: {response_json}")
                
                # 添加调试信息
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    choice = response_json['choices'][0]
                    content_response = choice.get('message', {}).get('content', '')
                    finish_reason = choice.get('finish_reason', 'unknown')
                    
                    api_logger.info(f"响应内容长度: {len(content_response)} 字符")
                    api_logger.info(f"完成原因: {finish_reason}")
                    api_logger.info(f"响应前500字符: {content_response[:500]}")
                    
                    print(f"AI响应内容长度: {len(content_response)}")
                    print(f"AI响应前200字符: {content_response[:200]}")
                    
                    # 检查是否因为token限制被截断
                    if finish_reason == 'length':
                        warning_msg = "警告：响应因达到最大token限制而被截断"
                        api_logger.warning(warning_msg)
                        print(warning_msg)
                        
                    # 记录token使用情况
                    if 'usage' in response_json:
                        usage = response_json['usage']
                        api_logger.info(f"Token使用情况: {usage}")
                        
                return response_json
            else:
                error_msg = f"硅基流动API请求失败，状态码: {res.status}"
                api_logger.error(error_msg)
                api_logger.error(f"错误响应内容: {response_text}")
                print(error_msg)
                print(f"响应内容: {response_text}")
                return None
                
        except Exception as e:
            error_msg = f"发送到硅基流动API时出错: {e}"
            api_logger.error(error_msg, exc_info=True)
            print(error_msg)
            return None
        finally:
            try:
                conn.close()
                api_logger.info("HTTP连接已关闭")
            except:
                pass