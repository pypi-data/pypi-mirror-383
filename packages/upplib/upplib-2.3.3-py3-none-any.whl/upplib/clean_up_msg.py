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
    s = thread_id_str
    if len(thread_id_str) >= 3:
        s = thread_id_str[-2:]
    if len(thread_id_str) == 1:
        s = '-' + thread_id_str
    if len(thread_id_str) == 0:
        s = '--'
    return f' -{s}- '


def clean_up_msg_1(msg: str = None) -> str:
    try:
        """
            2025-09-28T19:38:41.146-06:00 com.leo.digest.aop.ApiLogAspect - traceId: - (catTraceId:rcs-gateway-0a0f2154-488625-102) - ===>API GatewayFacadeImpl#gatewayRequest START
            ->
            2025-09-28T20:09:52.390-06:00 o.rcs.biz.limiter.XLimitSwitc - rcs-gateway-0a0f2154-488625-102 - xlimit No current limiter configured，key=mobilewalla_mbmultiagents


            2025-09-29T10:26:55.161-06:00 c.c.f.a.spring.annotation.SpringValueProcessor - traceId: - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            ->
            2025-09-29T10:26:55.161-06:00 annotation.SpringValueProcessor - - Monitoring key: spring.mvc.servlet.path, beanName: swaggerWelcome, field: org.springdoc.webmvc.ui.SwaggerWelcomeWebMvc.mvcServletPath
            
            
            2025-10-09T11:29:30.561+08:00 [http-nio-8080-exec-5097] INFO  com.leo.rcs.biz.aspect.RcsReportAspect - traceId: - (catTraceId:datafeaturecore-0a5a030c-488883-287895) - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
            ->
            2025-10-09T11:29:30.561+08:00 -97- INFO  com.leo.rcs.biz.aspect.RcsReportAspect - datafeaturecore-0a5a030c-488883-287895 - RequestBody:{"bizData":{"user_id":1073850014231710218,"gaid":"364de12f-2fc9-4769-b2b6-e0b47bdf841d"},"extContext":{"mainDecisionId":"20251009112924085WITHDRAW02124","standardScene":"WITHDRAW"},"ignoreCache":false,"ignoreStatus":false,"interfaceId":"mobilewalla","methodId":"multiagents"}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        # CAT_TRACE_ID_DEMO = '(catTraceId:rcs-gateway-0a0f2154-488625-102)'
        SEP_S = '- traceId: -'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        msg10 = msg1[0].strip()
        thread_id = ' '
        pattern = r'nio-(\d+)-exec-(\d+)'
        match = re.search(pattern, msg10)
        if match:
            thread_id = get_thread_id_for_log(match.group(2))
        method = msg10[-31:]
        other = msg1[1].strip()
        if len(method) < 31:
            method = ' ' * (31 - len(method)) + method
        if other.strip().startswith('(catTraceId:'):
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg1[1]).group(1)
            other = other[other.find(trace_id) + len(trace_id) + 1:].strip()
        else:
            trace_id = ''
            other = other.strip()
        if other.strip().startswith('- '):
            other = other[2:].strip()
        return f'{time}{thread_id}{method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_2(msg: str = None) -> str:
    try:
        """
            2025-10-09T13:45:49.687+08:00 INFO 8 --- [nio-8080-exec-4] c.l.r.b.s.device.impl.DeviceServiceImpl  : (catTraceId:customer-product-0a5a0329-488885-107496) - checkDeviceId lock key: 1073852969169211259
            ->
            2025-10-09T13:45:49.687+08:00 -04- c.l.r.b.s.device.impl.DeviceServiceImpl - customer-product-0a5a0329-488885-107496 - checkDeviceId lock key: 1073852969169211259
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = ': (catTraceId:'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        msg10 = msg1[0].strip()
        thread_id = ' '
        pattern = r'nio-(\d+)-exec-(\d+)'
        match = re.search(pattern, msg10)
        if match:
            thread_id = get_thread_id_for_log(match.group(2))
        method = msg10.strip()[-31:]
        other = msg1[1].strip()
        if len(method) < 31:
            method = ' ' * (31 - len(method)) + method
        trace_id = other[0:other.find(') - ')].strip()
        other = other[other.find(trace_id) + len(trace_id) + 3:].strip()
        return f'{time}{thread_id}{method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_3(msg: str = None) -> str:
    try:
        """
            2025-10-09T14:25:28.096+07:00 INFO com.itn.idn.review.aop.LogAspect - traceId:db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
            ->
            2025-10-09T14:25:28.096+07:00 com.itn.idn.review.aop.LogAspect - db57046b7cba9d5c55fa5ff93727c4df - ReviewBackController.queryCreditCasesByUserIdsV2: request log info-------------> {"userIds":[1011450014961537063]}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = ' - traceId:'
        time = msg[0:len(TIME_DEMO)]
        msg1 = msg[len(TIME_DEMO):].split(SEP_S)
        method = msg1[0].strip()[-31:]
        other = msg1[1].strip()
        if len(method) < 31:
            method = ' ' * (31 - len(method)) + method
        trace_id = other[0:other.find(' - ')].strip()
        other = other[other.find(trace_id) + len(trace_id) + 2:].strip()
        return f'{time} {method} - {trace_id} - {other}'
    except Exception as e:
        return msg


def clean_up_msg_4(msg: str = None) -> str:
    try:
        """
            2025-10-09T15:00:33.751+07:00 INFO [TID: N/A] [8] [http-nio-10009-exec-1] [GatewayController] [WITHDRAW-1080478239721884577] Call response: length=632929
            ->
            2025-10-09T15:00:33.751+07:00 -01- GatewayController - WITHDRAW-1080478239721884577 - Call response: length=632929
            
            2025-10-10T09:14:47.178+07:00 INFO [TID: N/A] [8] [strategyAsyncExecutor-26] [DefaultLogHandler] [-] [Forest] Request (okhttp3): \n\t[Type Change]: GET -> POST\n\tPOST http://xdecisionengine-svc.java/engine/apply HTTP\n\tHeaders: \n\t\trequester: rcsbatch\n\t\tapp: 360Kredi\n\t\tbiz_flow_number: 28085377ee25467ea3941b1e3f681c55\n\t\tinner_app: 360Kredi\n\t\ttpCode: rcsBatch\n\t\treport_id: 7721fe0bbfc0415c94e2b91dfa622aca\n\t\trequestId: 28085377ee25467ea3941b1e3f681c55\n\t\tbiz_type: MARKET_MODEL_CALCULATE\n\t\tseq_id: 11f0724b4a0b48a8a5e9cdbe54bc22d7\n\t\tsource_type: other\n\t\ttimestamp: 1760046298655\n\t\tscene: MARKET_MODEL_CALCULATE\n\t\tContent-Type: application/json\n\tBody: {"engineCode":"jcl_20250917000001","organId":20,"fields":{"app":"360Kredi","requester":"rcsbatch","biz_flow_number":"28085377ee25467ea3941b1e3f681c55","inner_app":"360Kredi","user_id":1021847804368362617,"report_id":"7721fe0bbfc0415c94e2b91dfa622aca","cust_no":"1021847804368362617","biz_type":"MARKET_MODEL_CALCULATE","seq_id":"11f0724b4a0b48a8a5e9cdbe54bc22d7","source_type":"other","user_no":"1021847804368362617","timestamp":1760046298655}}
            ->
            2025-10-10T09:14:47.178+07:00 -26- DefaultLogHandler - - [Forest] Request (okhttp3): \n\t[Type Change]: GET -> POST\n\tPOST http://xdecisionengine-svc.java/engine/apply HTTP\n\tHeaders: \n\t\trequester: rcsbatch\n\t\tapp: 360Kredi\n\t\tbiz_flow_number: 28085377ee25467ea3941b1e3f681c55\n\t\tinner_app: 360Kredi\n\t\ttpCode: rcsBatch\n\t\treport_id: 7721fe0bbfc0415c94e2b91dfa622aca\n\t\trequestId: 28085377ee25467ea3941b1e3f681c55\n\t\tbiz_type: MARKET_MODEL_CALCULATE\n\t\tseq_id: 11f0724b4a0b48a8a5e9cdbe54bc22d7\n\t\tsource_type: other\n\t\ttimestamp: 1760046298655\n\t\tscene: MARKET_MODEL_CALCULATE\n\t\tContent-Type: application/json\n\tBody: {"engineCode":"jcl_20250917000001","organId":20,"fields":{"app":"360Kredi","requester":"rcsbatch","biz_flow_number":"28085377ee25467ea3941b1e3f681c55","inner_app":"360Kredi","user_id":1021847804368362617,"report_id":"7721fe0bbfc0415c94e2b91dfa622aca","cust_no":"1021847804368362617","biz_type":"MARKET_MODEL_CALCULATE","seq_id":"11f0724b4a0b48a8a5e9cdbe54bc22d7","source_type":"other","user_no":"1021847804368362617","timestamp":1760046298655}}
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        SEP_S = '] '
        time = msg[0:len(TIME_DEMO)]
        msg0 = msg[len(TIME_DEMO):].strip()
        msg1 = msg0.split(SEP_S)
        try:
            thread_id = get_thread_id_for_log(msg1[2].strip().split('-')[-1])
        except Exception:
            thread_id = ' '
        method = msg1[3].strip().strip()[-15:]
        if len(method) < 15:
            method = ' ' * (15 - len(method)) + method
        trace_id = msg1[4].strip()[msg1[4].strip().find('[') + 1:]
        other = msg0[len(SEP_S.join(msg1[0:5])) + 1:].strip()
        return f'{time}{thread_id}{method} - {trace_id} - {other}'
    except Exception:
        return msg


def clean_up_msg_5(msg: str = None) -> str:
    try:
        """
            2025-10-10T09:59:36.118+07:00 [http-nio-8080-exec-13][AUDIT.1070150904958674814][20251010095936118AUDIT04869][jcl_20250109000001][][MAIN] INFO - (catTraceId:xdecisionengine-0a1e0845-488906-400194) - putAll to context ,value={"app":"kredi","ip":"192.168.1.8","session_id":"","source_type":"ANDROID","product_name":"kredi"} - cn.xinfei.xdecision.engine.domain.context.PipelineContextHolder.()
            ->
            2025-10-10T09:59:36.118+07:00 -13- n.context.PipelineContextHolder - xdecisionengine-0a1e0845-488906-400194 - putAll to context ,value={"app":"kredi","ip":"192.168.1.8","session_id":"","source_type":"ANDROID","product_name":"kredi"}
        
            2025-10-10T13:45:56.000+08:00 [xdecision-reentry-server_2-thread_757][1080554879087872098][20251010135455914APPLY03025][jcl_20240927000001_59][][] INFO -  Release distributed lock，clientId=10.90.0.132,lockKey=LOCK_PENDING_REENTRY_20251010135455914APPLY03025 - cn.xinfei.xdecision.redis.RedisLock.()
            ->
            2025-10-10T13:45:56.000+08:00 -57- infei.xdecision.redis.RedisLock - - Release distributed lock，clientId=10.90.0.132,lockKey=LOCK_PENDING_REENTRY_20251010135455914APPLY03025
            
            2025-10-10T13:55:57.000+08:00 [xdecision-decision-table_8-thread_460][1090894420147560136][20251010140508949REPAY_ADJUST03055_1_1][jcl_20250807000007_65][jcb_20250817000001][CHILD] ERROR- custNo is empty - cn.xinfei.xdecision.engine.domain.context.PipelineContextHolder.()
            ->
            2025-10-10T13:55:57.000+08:00 -60- n.context.PipelineContextHolder - ERROR- custNo is empty
        """
        TIME_DEMO = '2025-09-28T20:09:52.390-06:00'
        time = msg[0:len(TIME_DEMO)]
        msg0 = msg[len(TIME_DEMO):].strip()
        try:
            thread_id = get_thread_id_for_log(msg0.split('][')[0].strip().split('-')[-1])
        except Exception:
            thread_id = ' '
        method_raw = msg0.split(' - ')[-1].strip()
        method = method_raw.replace('.()', '')[-31:]
        if len(method) < 31:
            method = ' ' * (31 - len(method)) + method
        trace_id = ''
        trace_raw = ''
        if '(catTraceId:' in msg0:
            trace_id = re.search(r'\(catTraceId:([^)]+)\)', msg0).group(1)
            trace_raw = trace_id
        else:
            for sep in ['] INFO - ', '] ERROR- ']:
                if sep in msg0:
                    trace_raw = sep
                    trace_id = re.sub(r'[^a-zA-Z0-9]', '', sep)
                    trace_id = '-' * (5 - len(trace_id)) + trace_id
                    break
        other = msg0[msg0.find(trace_raw) + len(trace_raw) + 3:].split(' - ' + method_raw)[0].strip()
        return f'{time}{thread_id}{method} - {trace_id} - {other}'
    except Exception:
        return msg
