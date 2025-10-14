
from fastapi import APIRouter
from diglife.core import DigitalAvatar
from diglife.models import *
from diglife.log import Log
logger = Log.logger

import os
running_log = logger.info


router = APIRouter(tags=["optimize"])

da = DigitalAvatar(model_name = os.getenv("llm_model_name"),
                              api_key = os.getenv("llm_api_key"))

@router.post("/user_overview")
async def user_overview_server(request: UseroverviewRequests):
    """
    用户概述 以后再说
    """
    running_log("running user_overview_server")
    memory_cards = request.model_dump()["memory_cards"]
    result = await da.auser_overview(
        action = request.action,
        old_overview=request.old_overview, 
        memory_cards=memory_cards,
        type = IntellectType.inference,
        demand = "",
        version = None,
    )  # 包裹的内核函数

    return {"overview": result}


