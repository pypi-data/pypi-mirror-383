
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager


from pydantic import BaseModel, Field, model_validator
import argparse
import uvicorn
import uuid
from temp_optimize.log import Log
from temp_optimize.core import get_prompt, save_prompt
from temp_optimize.core import inference_prompt, train_prompt, summary_prompt,get_latest_version


# 应用程序生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


default=8009


app = FastAPI(
    lifespan=lifespan,
    title="LLM Optimize",
    description="用于调整提示词的服务",
    version="1.0.1",
)


# --- Configure CORS ---
origins = [
    "*", # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True, # Allows cookies/authorization headers
    allow_methods=["*"],    # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---


@app.get("/")
async def root():
    """ x """
    return {"message": "LLM Service is running."}

@app.get("/inference_prompt")
async def inference_prompt_server(prompt_id : str,input : str):
    result = inference_prompt(prompt_id = prompt_id,
               input = input)
    return result 

@app.get("/train_prompt")
async def train_prompt_server(prompt_id : str,
                              demand : str,
                              input :str):
    result = train_prompt(prompt_id = prompt_id,
               demand = demand,
               input = input)
    return result 

@app.get("/summary_prompt")
async def summary_prompt_server(prompt_id : str):
    result = summary_prompt(prompt_id = prompt_id)
    return result 

@app.get("/latest_version")
async def get_latest_version_server(prompt_id : str):
    result = get_latest_version(prompt_id = prompt_id)
    return result 

@app.get("/get_prompt")
async def get_prompt_server(prompt_id : str,version : str = None):
    result = get_prompt(prompt_id = prompt_id,
               version = version)
    return result 

@app.get("/save_prompt")
async def save_prompt_server(prompt_id : str,prompt : str):
    result = save_prompt(prompt_id = prompt_id,
               new_prompt = prompt)
    return result 



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=default,
        help=f'Specify alternate port [default: {default}]'
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        '--dev',
        action='store_true', # 当存在 --dev 时，该值为 True
        help='Run in development mode (default).'
    )

    # 添加 --prod 选项
    group.add_argument(
        '--prod',
        action='store_true', # 当存在 --prod 时，该值为 True
        help='Run in production mode.'
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level('debug',env = env)
        reload = True
        app_import_string = f"{__package__}.__main__:app" # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level('info',env = env)# ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app
    

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string,
        host="0.0.0.0",
        port=port,
        reload=reload  # 启用热重载
    )
