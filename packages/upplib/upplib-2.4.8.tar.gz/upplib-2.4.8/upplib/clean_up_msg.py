from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union


def clean_up_msg(msg: str = None, clean_up_type: int = 1) -> str:
    if msg is None:
        return ''
    formatters: list[Callable[[str], Optional[str]]] = [
        clean_up_msg_1,
        clean_up_msg_2,
        clean_up_msg_3,
        clean_up_msg_4,
        clean_up_msg_5,
    ]
    formatter_map: dict[int, Callable[[str], Optional[str]]] = {
        i + 1: formatter for i, formatter in enumerate(formatters)
    }
    if clean_up_type in formatter_map:
        return formatter_map[clean_up_type](msg)
    return msg


def get_thread_id_for_log(thread_id_str: str = None) -> str:
    """
        格式化线程 ID 用于日志输出。
        规则：
          - None 或空字符串 -> '--'
          - 长度1 -> '-x'
          - 长度≥2 -> 最后两位
        返回格式: ' -XX- '
        """
    if not thread_id_str:  # 处理 None 和 空字符串
        suffix = '--'
    elif len(thread_id_str) == 1:
        suffix = '-' + thread_id_str
    else:  # 长度 >= 2
        suffix = thread_id_str[-2:]
    return f' -{suffix}- '


def clean_up_msg_1(msg: str = None) -> str:
    try:
        """
            2025-09-28T19:38:41.146-06:00 com.leo.digest.aop.ApiLogAspect - traceId: - (catTraceId:rcs-gateway-0a0f2154-488625-102) - ===>API GatewayFacadeImpl#gatewayRequest START
            2025-09-28T19:38:41.146-06:00 com.leo.digest.aop.ApiLogAspect - rcs-gateway-0a0f2154-488625-102 - ===>API GatewayFacadeImpl#gatewayRequest START

            2025-09-29T10:26:55.161-06:00 c.c.f.a.spring.annotation.SpringValueProcessor - traceId: - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            2025-09-29T10:26:55.161-06:00 annotation.SpringValueProcessor - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            
            2025-10-09T11:29:30.561+08:00 [http-nio-8080-exec-5097] INFO  com.leo.rcs.biz.aspect.RcsReportAspect - traceId: - (catTraceId:datafeaturecore-0a5a030c-488883-287895) - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
            2025-10-09T11:29:30.561+08:00 -97- .rcs.biz.aspect.RcsReportAspect - datafeaturecore-0a5a030c-488883-287895 - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
        """
        time1, _, msg0 = msg.strip().partition(' ')
        method, _, other = msg0.strip().partition(' - traceId: - ')
        thread_id = get_thread_id_for_log(method.strip().partition('] ')[0].rpartition('-')[2]) if '] ' in method else ' '
        method = method.strip()[-31:].rjust(31)
        if '(catTraceId:' in other:
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', other).group(1).strip()
            other = other.strip().partition(trace_id)[2][3:].strip()
        else:
            trace_id = ''
        other = other[2:].strip() if other.strip().startswith('- ') else other.strip()
        trace_id = f' - {trace_id} - ' if len(trace_id) > 0 else ' - '
        return f'{time1}{thread_id}{method}{trace_id}{other}'
    except:
        return msg


def clean_up_msg_2(msg: str = None) -> str:
    try:
        """
            2025-10-09T13:45:49.687123+08:00 INFO 8 --- [nio-8080-exec-4] c.l.r.b.s.device.impl.DeviceServiceImpl  : (catTraceId:customer-product-0a5a0329-488885-107496) - checkDeviceId lock key: 1073852969169211259
            2025-10-09T13:45:49.687123+08:00 --4- s.device.impl.DeviceServiceImpl - customer-product-0a5a0329-488885-107496 - checkDeviceId lock key: 1073852969169211259
            
            2025-10-10T20:16:30.071887+08:00 INFO 8 --- [ay-task-query-5] c.l.r.b.s.d.s.i.DelayTaskCoreServiceImpl : DelayTaskCoreServiceImpl queryTaskResult response: {"sign":null,"hitResultList":[],"branchRejectInfo":[]}
            2025-10-10T20:16:30.071887+08:00 --5- .d.s.i.DelayTaskCoreServiceImpl - DelayTaskCoreServiceImpl queryTaskResult response: {"sign":null,"hitResultList":[],"branchRejectInfo":[]}
        """
        time1, _, msg0 = msg.strip().partition(' ')
        thread_id = get_thread_id_for_log(msg0.strip().rpartition('] ')[0].rpartition('-')[2])
        method, _, other = msg0.strip().rpartition(' : ')
        method = method.strip()[-31:].rjust(31)
        trace_id = ''
        if '(catTraceId:' in other:
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', other).group(1)
            other = other.strip().partition(trace_id)[2][3:].strip()
        other = other[1:].strip() if other.startswith(':') else other
        trace_id = f' - {trace_id} - ' if len(trace_id) > 0 else ' - '
        return f'{time1}{thread_id}{method}{trace_id}{other}'
    except:
        return msg


def clean_up_msg_3(msg: str = None) -> str:
    try:
        """
            2025-10-09T14:25:28.096+07:00 INFO com.itn.idn.review.aop.LogAspect - traceId:db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
            2025-10-09T14:25:28.096+07:00 om.itn.idn.review.aop.LogAspect - db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
        """
        SEP_S = ' - traceId:'
        time1, _, msg0 = msg.strip().partition(' ')
        msg1 = msg0.strip().split(SEP_S)
        method = ' ' + msg1[0].strip()[-31:].rjust(31)
        trace_id, _, other = msg1[1].strip().partition(' - ')
        trace_id = f' - {trace_id} - ' if len(trace_id) > 0 else ' - '
        return f'{time1}{method}{trace_id}{other}'
    except:
        return msg


def clean_up_msg_4(msg: str = None) -> str:
    try:
        """
            2025-10-11T10:49:24.071000+07:00 INFO [TID: N/A] [8] [strategyAsyncExecutor-1] [FlowExecutor] [-] [33f7a5cfed3548f9aa3cc39079d1e407]:(catTraceId:rcs-provider-server-0a1e0d61-488931-966531) - requestId has generated
            2025-10-11T10:49:24.071000+07:00 --1-    FlowExecutor - rcs-provider-server-0a1e0d61-488931-966531 - requestId has generated
            
            2025-10-09T15:00:33.751000+07:00 INFO [TID: N/A] [8] [http-nio-10009-exec-1] [GatewayController] [WITHDRAW-1080478239721884577] Call response: length=632929
            2025-10-09T15:00:33.751000+07:00 --1- tewayController - WITHDRAW-1080478239721884577 - Call response: length=632929
            
            2025-10-10T09:14:47.178000+07:00 INFO [TID: N/A] [8] [strategyAsyncExecutor-26] [DefaultLogHandler] [-] [Forest] Request (okhttp3): [Type Change]: GET -> POSTPOST http://xdecisionengine-svc.java/engine/apply HTTPHeaders: \trequester: rcsbatch\tapp: 360Kredi\tbiz_flow_number: 28085377ee25467ea3941b1e3f681c55\tinner_app: 360Kredi\ttpCode: rcsBatch\treport_id: 7721fe0bbfc0415c94e2b91dfa622aca\trequestId: 28085377ee25467ea3941b1e3f681c55\tbiz_type: MARKET_MODEL_CALCULATE\tseq_id: 11f0724b4a0b48a8a5e9cdbe54bc22d7\tsource_type: other\ttimestamp: 1760046298655\tscene: MARKET_MODEL_CALCULATE\tContent-Type: application/jsonBody: {"engineCode":"jcl_20250917000001","organId":20,"fields":{"app":"360Kredi","requester":"rcsbatch","biz_flow_number":"28085377ee25467ea3941b1e3f681c55","inner_app":"360Kredi","user_id":1021847804368362617,"report_id":"7721fe0bbfc0415c94e2b91dfa622aca","cust_no":"1021847804368362617","biz_type":"MARKET_MODEL_CALCULATE","seq_id":"11f0724b4a0b48a8a5e9cdbe54bc22d7","source_type":"other","user_no":"1021847804368362617","timestamp":1760046298655}}
            2025-10-10T09:14:47.178000+07:00 -26- faultLogHandler - [-] [Forest] Request (okhttp3): [Type Change]: GET -> POSTPOST http://xdecisionengine-svc.java/engine/apply HTTPHeaders: 	requester: rcsbatch	app: 360Kredi	biz_flow_number: 28085377ee25467ea3941b1e3f681c55	inner_app: 360Kredi	tpCode: rcsBatch	report_id: 7721fe0bbfc0415c94e2b91dfa622aca	requestId: 28085377ee25467ea3941b1e3f681c55	biz_type: MARKET_MODEL_CALCULATE	seq_id: 11f0724b4a0b48a8a5e9cdbe54bc22d7	source_type: other	timestamp: 1760046298655	scene: MARKET_MODEL_CALCULATE	Content-Type: application/jsonBody: {"engineCode":"jcl_20250917000001","organId":20,"fields":{"app":"360Kredi","requester":"rcsbatch","biz_flow_number":"28085377ee25467ea3941b1e3f681c55","inner_app":"360Kredi","user_id":1021847804368362617,"report_id":"7721fe0bbfc0415c94e2b91dfa622aca","cust_no":"1021847804368362617","biz_type":"MARKET_MODEL_CALCULATE","seq_id":"11f0724b4a0b48a8a5e9cdbe54bc22d7","source_type":"other","user_no":"1021847804368362617","timestamp":1760046298655}}
        """
        SEP_S = '] '
        time1, _, msg0 = msg.strip().partition(' ')
        msg1 = msg0.split(SEP_S)
        thread_id = get_thread_id_for_log(msg1[2].strip().rpartition('-')[2])
        method = msg1[3].strip().strip()[-15:].strip().replace('[', '').rjust(15)
        if ']:(catTraceId:' in msg1[5]:
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg0).group(1)
            other = msg0.partition(trace_id)[2][3:].strip()
        else:
            trace_id = msg1[4].strip().partition('[')[2].strip()
            trace_id = trace_id[1:].strip() if trace_id.startswith('-') else trace_id
            other = msg0.strip().partition(method)[2][1:].strip() if len(trace_id) == 0 else msg0.strip().partition(trace_id)[2][1:].strip()
        trace_id = f' - {trace_id} - ' if len(trace_id) > 0 else ' - '
        return f'{time1}{thread_id}{method}{trace_id}{other}'
    except:
        return msg


def clean_up_msg_5(msg: str = None) -> str:
    try:
        """
            2025-10-10T09:59:36.118111+07:00 [http-nio-8080-exec-13][AUDIT.1070150904958674814][20251010095936118AUDIT04869][jcl_20250109000001][][MAIN] INFO - (catTraceId:xdecisionengine-0a1e0845-488906-400194) - putAll to context ,value={"app":"kredi","ip":"192.168.1.8","session_id":"","source_type":"ANDROID","product_name":"kredi"} - cn.xinfei.xdecision.engine.domain.context.PipelineContextHolder.()
            2025-10-10T09:59:36.118111+07:00 -13- n.context.PipelineContextHolder - xdecisionengine-0a1e0845-488906-400194 - putAll to context ,value={"app":"kredi","ip":"192.168.1.8","session_id":"","source_type":"ANDROID","product_name":"kredi"}
        
            2025-10-10T13:45:56+08:00 [xdecision-reentry-server_2-thread_757][1080554879087872098][20251010135455914APPLY03025][jcl_20240927000001_59][][] INFO -  Release distributed lock，clientId=10.90.0.132,lockKey=LOCK_PENDING_REENTRY_20251010135455914APPLY03025 - cn.xinfei.xdecision.redis.RedisLock.()
            2025-10-10T13:45:56+08:00 -57- infei.xdecision.redis.RedisLock - -INFO - Release distributed lock，clientId=10.90.0.132,lockKey=LOCK_PENDING_REENTRY_20251010135455914APPLY03025
            
            2025-10-10T13:55:57+08:00 [xdecision-decision-table_8-thread_460][1090894420147560136][20251010140508949REPAY_ADJUST03055_1_1][jcl_20250807000007_65][jcb_20250817000001][CHILD] ERROR- custNo is empty - cn.xinfei.xdecision.engine.domain.context.PipelineContextHolder.()
            2025-10-10T13:55:57+08:00 -60- n.context.PipelineContextHolder - ERROR - custNo is empty
        """
        time1, _, msg0 = msg.strip().partition(' ')
        thread_id = get_thread_id_for_log(msg0.strip().partition('][')[0].strip().rpartition('-')[2])
        msg0, _, method = msg0.rpartition(' - ')
        method = method.strip().replace('.()', '')[-31:].rjust(31)
        trace_id = ''
        other = ''
        if '(catTraceId:' in msg0:
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg0).group(1)
            other = msg0.partition(trace_id)[2][3:].strip()
        else:
            for sep in ['] INFO - ', '] ERROR- ', '] WARN - ']:
                if sep in msg0:
                    other = msg0.partition(sep)[2].strip()
                    trace_id = re.sub(r'[^a-zA-Z0-9]', '', sep).rjust(5, '-')
                    break
        trace_id = f' - {trace_id} - ' if len(trace_id) > 0 else ' - '
        return f'{time1}{thread_id}{method}{trace_id}{other}'
    except:
        return msg
