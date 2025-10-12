import asyncio
import json
import time
import zlib
from typing import Literal, Union

from aiohttp import ClientWebSocketResponse
from aiohttp.client_exceptions import ContentTypeError
import pybotters


def callback(msg, ws: ClientWebSocketResponse = None):
    # print("Received message:", msg)
    decompressed = zlib.decompress(msg, 16 + zlib.MAX_WBITS)
    text = decompressed.decode("utf-8")
    print(f"Decoded text: {text}")

def callback2(msg, ws: ClientWebSocketResponse = None):
    # print("Received message:", msg)
    # print(str(msg))
    data = json.loads(msg)  
    print(data.get('y'))


async def main():
    async with pybotters.Client() as client:
        # webData2
        client.ws_connect(
            "wss://ccws.rerrkvifj.com/ws/V3/",
            send_json={
                "dataType": 3,
                "depth": 200,
                "pair": "arb_usdt",
                "action": "subscribe",
                "subscribe": "depth",
                "msgType": 2,
                "limit": 10,
                "type": 10000,
            },
            hdlr_bytes=callback,
        )

        while True:
            await asyncio.sleep(1)


async def main2():
    async with pybotters.Client() as client:
        # webData2
        # x 为chanel, y为唯一标识, a为参数, z为版本号
        wsapp = client.ws_connect(
            "wss://uuws.rerrkvifj.com/ws/v3",
            send_json={'x': 3, 'y': '3000000001', 'a': {'i': 'SOLUSDT_0.01_25'}, 'z': 1},
            hdlr_bytes=callback2,
        )
        await wsapp._event.wait()

        async with pybotters.Client() as client2:
            client2.ws_connect(
                "wss://uuws.rerrkvifj.com/ws/v3",
                send_json={'x': 3, 'y': '3000000002', 'a': {'i': 'XRPUSDT_0.0001_25'}, 'z': 1},
                hdlr_bytes=callback2,
            )
            await wsapp.current_ws.send_json({'x': 3, 'y': '3000000002', 'a': {'i': 'XRPUSDT_0.0001_25'}, 'z': 1})

        while True:
            await asyncio.sleep(1)

from hyperquant.broker.lbank import Lbank

async def test_broker():
    async with pybotters.Client() as client:
        async with Lbank(client) as lb:
            print(lb.store.detail.find())


async def test_broker_detail():
    async with pybotters.Client() as client: 
        data = await client.post(
            "https://uuapi.rerrkvifj.com/cfd/agg/v1/instrument",
            headers={"source": "4", "versionflage": "true"},
            json={
            "ProductGroup": "SwapU"
            }
        ) 
        res = await data.json()
        print(res)

async def test_broker_subbook():
    async with pybotters.Client() as client:
        async with Lbank(client) as lb:
            symbols = [item['symbol'] for item in lb.store.detail.find()]
            symbols = symbols[10:30]
            print(symbols)

            await lb.sub_orderbook(symbols, limit=1)
            
            while True:
                print(lb.store.book.find({
                    "s": symbols[8]
                }))
                await asyncio.sleep(1)

async def test_update():
    async with pybotters.Client(apis='./apis.json') as client:
        async with Lbank(client) as lb:
            await lb.update('position')
            print(lb.store.position.find())
            # await lb.update('balance')
            # print(lb.store.balance.find())
            # await lb.update('detail')
            # print(lb.store.detail.find())
            # await lb.update('orders')
            # await lb.update('orders_finish')
  
            # print(lb.store.order_finish.find({
            #     'order_id': '1000632478428573'
            # }))

async def test_place():
    async with pybotters.Client(apis='./apis.json') as client:
        async with Lbank(client) as lb:
            order = await lb.place_order(
                "SOLUSDT",
                direction="buy",
                order_type='limit_gtc',
                price=182,
                volume=0.03,
            )
            print(order)



async def test_cancel():
    async with pybotters.Client(apis='./apis.json') as client:
        async with Lbank(client) as lb:
            res = await lb.cancel_order("1000624020664540")
            print(res)


async def order_sync_polling(
    broker: Lbank,
    *,
    symbol: str,
    direction: Literal["buy", "sell"] = "buy",
    order_type: Literal["market", "limit_gtc", "limit_ioc", "limit_GTC", "limit_IOC"] = "limit_gtc",
    price: float | None = None,
    volume: float | None = None,
    window_sec: float = 5.0,
    grace_sec: float = 5.0,
    poll_interval: float = 0.5,
) -> Union[dict, None]:
    """
    由于 LBank 暂无订单推送，这里通过 REST ``orders`` 与 ``position`` 查询实现订单同步，可在不同状态下返回仓位快照。

    - window_sec: 主轮询窗口，订单若持续存在则触发撤单流程；
    - grace_sec: 撤单后的额外等待窗口；
    - 返回值示例：
        .. code:: json

            {
                "position_id": "1000633222380983",
                "bus_id": "1001770970175249",
                "symbol": "SOLUSDT",
                "side": "long",
                "quantity": "0.06",
                "available": "0.0",
                "avg_price": "183.62",
                "entry_price": "183.62",
                "leverage": "100.0",
                "liquidation_price": "0",
                "margin_used": "0.110175",
                "unrealized_pnl": "0.0",
                "realized_pnl": "0.0",
                "update_time": "1760195121",
                "insert_time": "1758806193"
            } 
    """

    norm_type = order_type.lower()
    if norm_type not in {"market", "limit_gtc", "limit_ioc"}:
        raise ValueError(f"unsupported order_type: {order_type}")

    if norm_type != "market" and price is None:
        raise ValueError("price is required for limit orders")
    if volume is None:
        raise ValueError("volume is required for LBank orders")

    started = int(time.time() * 1000)
    resp = await broker.place_order(
        symbol,
        direction=direction,
        order_type=norm_type,
        price=price,
        volume=volume,
    )
    
    latency = int(time.time() * 1000) - started
    print(f"下单延迟 {latency} ms")

    order_id = (
        resp.get("orderSysID")
        or resp.get("OrderSysID")
        or resp.get("order_id")
        or resp.get("orderId")
    )
    if not order_id:
        raise RuntimeError(f"place_order 返回缺少 order_id: {resp}")

    position_id = (
        resp.get("PositionID")
        or resp.get("positionID")
        or resp.get("positionId")
    )

    async def _refresh_position(*, allow_symbol_fallback: bool) -> dict | None:
        try:
            await broker.update("position")
        except ContentTypeError:
            await asyncio.sleep(poll_interval)
            return None
        if position_id:
            pos = broker.store.position.get({"position_id": position_id})
            if pos and pos.get("avg_price") is not None:
                return pos
        if allow_symbol_fallback:
            candidates = broker.store.position.find({"symbol": symbol}) or []
            if candidates:
                pos = candidates[0]
                if pos and pos.get("avg_price") is not None:
                    return pos
        return None

    async def _poll_orders(timeout_sec: float, *, allow_symbol_fallback: bool) -> dict | None:
        nonlocal position_id
        order_seen = False
        async with asyncio.timeout(timeout_sec):
            while True:
                try:
                    await broker.update("orders")
                except ContentTypeError:
                    await asyncio.sleep(poll_interval)
                    continue
                snapshot = broker.store.orders.get({"order_id": order_id})
                if snapshot is None:
                    if not order_seen and not allow_symbol_fallback:
                        await asyncio.sleep(poll_interval)
                        continue
                    pos_snapshot = await _refresh_position(allow_symbol_fallback=allow_symbol_fallback)
                    if pos_snapshot is not None:
                        return pos_snapshot
                    await asyncio.sleep(poll_interval)
                    continue
                order_seen = True
                position_id = position_id or snapshot.get("position_id")
                await asyncio.sleep(poll_interval)

    try:
        polled_position = await _poll_orders(window_sec, allow_symbol_fallback=False)
        if polled_position:
            return polled_position
    except TimeoutError:
        pass

    for _attempt in range(3):
        try:
            await broker.cancel_order(order_id)
            break
        except Exception as e:
            if '不存在' in str(e):
                break
            else:
                print(f'撤单失败, 重试 {_attempt+1}/3: {e}')
    try:
        polled_position = await _poll_orders(grace_sec, allow_symbol_fallback=True)
        if polled_position:
            return polled_position
    except TimeoutError:
        pass

    # 超过宽限期仍没有仓位变更，尝试最后一次使用 symbol 兜底
    return await _refresh_position(allow_symbol_fallback=True)


async def test_order_sync_polling():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Lbank(client) as lb:
            await lb.sub_orderbook(["SOLUSDT"], limit=1)
            await lb.store.book.wait()
            bid0 = float(lb.store.book.find({"s": "SOLUSDT", 'S': 'b'})[0]['p'])
            bid0 = bid0 - 0.03
            print(bid0)

            result = await order_sync_polling(
                lb,
                symbol="SOLUSDT",
                direction="buy",
                order_type="limit_GTC",
                price=bid0,
                volume=0.03,
                window_sec=3.0,
                grace_sec=1,
                poll_interval=1
            )
            print(result)

async def test_query_order():
    async with pybotters.Client(apis='./apis.json') as client:
        async with Lbank(client) as lb:
            res = await lb.query_order("1000633129818889")
            print(res)

if __name__ == "__main__":
    asyncio.run(test_order_sync_polling())
