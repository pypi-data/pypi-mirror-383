import requests
import asyncio
import uuid
import logging
import os
from datetime import datetime
URL="https://apis.oneli.chat"
# URL="http://localhost:8085"

appurl="http://localhost:3000"
class AIClient:
    def __init__(self, client_id, client_secret, base_url=f'{URL}/v1/strategy'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        response = requests.post(
            f'{self.base_url}/auth/token',
            json={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
        )
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception('Failed to get access token')

    def generate_response(self, question,template_id, variables):
        response = requests.post(
            f'{self.base_url}/dynamic-response',
            json={
                'question':question,
                'template_id': template_id,
                'variables': variables
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json().get('response')
        else:
            return response.json()
            # raise Exception('Failed to generate response')

    def query_data(self, arg, template_id):
        response = requests.post(
            f'{self.base_url}/query-data',
            json={
                'arg': arg,
                'template_id': template_id
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            res=response.json()
            raise Exception(res['error'])
        

    def query_intention(self, question):
        response = requests.post(
            f'{self.base_url}/query-intention',
            json={
                'question': question
             
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            
            raise Exception('Failed to start intention query')
        
    def voc(self,productname,text):
        response = requests.post(
            f'{self.base_url}/voc',
            json={
                'productname': productname,
                'text':text
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start voc ')
        

    def spec(self,asin):
        response = requests.post(
            f'{self.base_url}/spec', 
            json={
                'asin': asin
               
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            res=response.json()
            raise Exception(f'Failed to start voc,reason:{res["error"]}')

     #选品建议   
    def suggestion(self, selected_products):
        response = requests.post(
            f'{self.base_url}/suggestion',
            json={
                "final_selected_products": selected_products
           
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start suggestion')
        
    async def competitor_analysis(self,missionid="",asins=[]):
        if not missionid:  # Check if missionid is empty
           missionid = str(uuid.uuid4())  # Generate a random UUID
        
        task_id = await self.get_competitive_data(missionid,asins)
       
        # logging.info(task_id)
    
        if task_id:
            
            task = await self.check_task_status(task_id)
            
            if task['status'] == "SUCCESS":
                ret=await self.analysis_details(missionid)
                return ret
        
       
    async def analysis_details(self,missionid):
        response = requests.post(
            f'{URL}/v1/conv/analysis/getid', 
            json={
                'missionid': missionid
               
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start analysis')

        
    async def get_competitive_data(self,missionid,asins):
        print(2)
        response = requests.post(
                f'{self.base_url}/competitor_analysis',
                json={
                    "asins": asins,
                    "missionid":missionid
            
                },
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
        
        if response.status_code == 200:
        
           result=response.json()
              
           return result['data']['task_id']
        else:
            raise Exception('Failed to request get_competitive_data')
     
    

    #获取所有asins
    async def productList(self,missionid):
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/productList",
            json={
                'missionid':missionid
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')



    async def getTaskStatus(self,taskId):
        data=await self.get_token()
        print(data['token'])
        response =requests.get(f"{URL}/v1/task/task_status/{taskId}",
                                headers={'Authorization': f"Bearer {data['token']}"})
        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        
    async def check_task_status(self,task_id):
        print(3)
        
        while True:
            try:
                
                response = await self.getTaskStatus(task_id)
                logging.info(response)
                status = response.get('status')
                logging.info(f"Task status: {status}")
                
                if status == "SUCCESS":
                    return {"status": "SUCCESS", "result": response.get('result')}
                    
            except Exception as error:
                logging.error(f"Error checking task status: {error}")
            
            await asyncio.sleep(1)  # Sleep for 1 second
     

    async def getGoodinfofromAmazon(self, asins,filename=None):
        if filename:
            locafile,filename=self.upload_file(filename)
            print(filename)
        
        
            response=self.create_asin_mission(locafile,filename)
            asins=response['asins']

        response = requests.post(
            f'{appurl}/api/run-task',
            json={
                "type": "asin",
                "data":{"asins": asins}
            
            },
        
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to run task')
        
    async def getAsinfromAmazon(self,title,keywords):
        missionid = str(uuid.uuid4()) 
        await self.update_mission("app_"+missionid, title,keywords)
        response = requests.post(
            f'{appurl}/api/run-task',
            json={
                "type": "list",
                "data":{"keywords":keywords,"missionid":"app_"+missionid}
            
            },
        
        )


        # if response.status_code == 202:
        # task_id = response.json()['task_id']
        # print(f"Task started with ID: {task_id}")
        # return task_id
        #print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to run task')

        
    def upload_file(self,file_path):
        url =f"{URL}/v1/task/upload"
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Uploaded filename: {data['filename']}")
            return file_name,data['filename']
        else:
            print(f"Upload failed: {response.text}")
            return None


    async def create_asin_mission(self,locafile,filename):
        # Start ASIN extraction process
        task_id = await self.create_asin_mission_api(filename)
        
        if task_id:
            task = await self.check_task_status(task_id)
            
            if task["status"] == "SUCCESS" and task["result"]["code"] == 200:
                missionid = task["result"]["missionid"]
                
                # Generate report title using AI
                gentitle_prompt = f"""
                以下是选品报告标题的关键要素
                今天是{datetime.now()}
                用户了提交了asin 列表,文件名称为{locafile}
                请生成亚马逊选品分析报告的标题
                """
                response_title = await self.call_ai_api([{"role": "user", "content": gentitle_prompt}])
                title = response_title["data"]
                
                # Update mission with generated title
                task_res = await self.update_mission(missionid, title, "无需关键词")
                
                if task_res["code"] == 200:
                    # Get ASIN list for the mission
                    res = await self.get_asin_list(missionid)
                    
                    if res["code"] == 200:
                        asinlist = res["data"]
                        asins = [item["asin"] for item in asinlist]
                        return {"missionid": missionid, "asins": asins}
        
        # Return None if any step fails
        return None
    


    # Example implementations of the required service functions
    async def create_asin_mission_api(self,filename: str) -> str:
     
        response = requests.post(
            f"{URL}/task/start_task",
            json={
                'name':"create_asin_mission",
                'data': {"file_name":filename},
            }
           
        )
        """Mock implementation - replace with actual API call"""
        if response.status_code == 200:
            res=response.json()
            return res['task_id']
        else:
            raise Exception('Failed to request task_status')
        

    # async def check_task_status(self,task_id: str) -> dict:
    #     response =requests.get(f"{URL}/task/task_status/{task_id}")
    #     if response.status_code == 200:
    #         ret= response.json()
    #         """Mock implementation - replace with actual status check"""
    #         return {
    #             "status": ret["status"],
    #             "result": {
    #                 "code": 200,
    #                 "missionid": ret["result"]["missionid"]
    #             }
    #         }
    #     else:
    #         raise Exception('Failed to request task_status')
    
    async def get_token(self):
        
        response =requests.get(f"{appurl}/api/gettoken")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        # response =requests.get(f"{URL}/system/sdklogin")
        # if response.status_code == 200:
        #     return response.json()
        # else:
        #     raise Exception('Failed to request task_status')

    async def call_ai_api(self,messages,tools):
        data=await self.get_token()
        print(data)
        response = requests.post(
            f"{URL}/agent/fn",
            json={"tools":tools,"messages":messages},
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

    async def update_mission(self,missionid: str, title: str, keywords: str) :
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/intertMissioinlist",
            json={
                'task_id':missionid,
                'report_title': title,
                'keywords': keywords,
                'task_status':'In Progress',
                'task_status_description':'数据采集任务开始'
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

    async def get_asin_list(self,missionid: str):
        response = requests.post(
            f"{URL}/conv/getid",
            json={
                'missionid':missionid}
           )

        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

        


    async def getallpageData(self,missionid: str) :
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/test/getallpageData",
            json={
                'missionid':missionid
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
            
        
    
 