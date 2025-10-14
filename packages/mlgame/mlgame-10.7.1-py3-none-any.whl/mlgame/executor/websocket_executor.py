import json
from mlgame.core.communication import TransitionCommManager
from mlgame.core.exceptions import ErrorEnum, GameError, MLProcessError
from mlgame.core.model import MLGameDataType
from mlgame.utils.logger import logger


import websockets


import asyncio


class WebSocketExecutor():
    def __init__(self, ws_uri, ws_comm: TransitionCommManager):
        # super().__init__(name="ws")
        logger.info("             ws_init ")
        self._proc_name = f"websocket({ws_uri}"
        self._ws_uri = ws_uri
        self._comm_manager = ws_comm
        self._recv_data_func = self._comm_manager.recv_from_game

    async def ws_start(self):
        async with websockets.connect(self._ws_uri, ping_interval=None) as websocket:
            logger.info("             ws_start")
            count = 0
            is_ready_to_end = False
            while 1:
                
                data = self._recv_data_func()
                # logger.debug()
                if data.type==MLGameDataType.END:
                    logger.debug(f"ws received from game:{data}")
                    break
                elif data.type == MLGameDataType.GAME_ERROR:
                    logger.error(f"ws received GameError:{data}")
                    error_data = data.data
                    
                    await websocket.send(data.model_dump_json())
                    # exit container
                    if error_data.error_type in [ErrorEnum.COMMAND_ERROR, ErrorEnum.GAME_EXEC_ERROR]:
                        logger.warning(f"ws received GameError:{error_data.error_type}")
                        system_message = {
                            "type": "system_message",
                            "data": {
                                "message": f"ws received GameError:{error_data.error_type.name} ws will be closed"
                            }
                        }
                        await websocket.send(json.dumps(system_message))
                        break
                        # os.system("pgrep -f 'tail -f /dev/null' | xargs kill")

                elif data.type == MLGameDataType.GAME_RESULT:
                    # raise a flag to recv data
                    # TODO replace with core.model
                    is_ready_to_end = True
                    logger.debug(f"GAME_RESULT :{data}")
                    await websocket.send(data.model_dump_json())
                else:
                    # print(data)
                    logger.debug(f"ws send :{data}")
                    if data.type == MLGameDataType.GAME_INFO:
                        await websocket.send(data.model_dump_json())
                    elif data.type == MLGameDataType.GAME_PROGRESS:
                        data.data={'frame':data.data.frame}
                        await websocket.send(data.model_dump_json())
                    elif data.type == MLGameDataType.SYSTEM_MSG:
                        await websocket.send(data.model_dump_json())
                    # count += 1
                    pass
                    # print(f'Send to ws : {count}:{data.keys()}')
                    #
                # make sure webservice got game result then mlgame is able to close websocket
                
                    
            while is_ready_to_end:
                # wait for game_result
                ws_recv_data = await websocket.recv()
                logger.info(f"ws received from django: {ws_recv_data}")
                if ws_recv_data == "game_result":
                    logger.info(f"< {ws_recv_data}")
                    await websocket.close()
                    is_ready_to_end = False
                    logger.info("close ws ")

                    # else:
                    #     await websocket.send(json.dumps({}))
            # time.sleep(1)
            # await websocket.close()

    def run(self):
        self._comm_manager.start_recv_obj_thread()
        try:
            asyncio.get_event_loop().run_until_complete(self.ws_start())
        except Exception as e:
            # exception = TransitionProcessError(self._proc_name, traceback.format_exc())
            self._comm_manager.send_exception(
                f"exception on {self._proc_name}")
            # catch connection error
            logger.exception("unknown exception in websocket executor")
        finally:
            logger.info("end ws ")