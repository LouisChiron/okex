import okex.account_api as account
import okex.spot_api as spot
import json
import datetime
import time

def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"

time1 = get_timestamp()

if __name__ == '__main__':
    # 交易所 个人私密Api信息
    api_key = "abd1b949-a105-45e9-90d5-e08d347535a6"
    secret_key = "C3817FD37890xxxxxxxxxxxxxxxxxxxxx"                                       #已隐藏部分
    passphrase = "yuxxxxxxx"                                                               #已隐藏部分
    accountAPI = account.AccountAPI(api_key, secret_key, passphrase, False)
    spotAPI = spot.SpotAPI(api_key, secret_key, passphrase, False)

    result = spotAPI.get_account_info()

    n = 0

#以下为提交购买部分
    size = '6400000'                             #size为交易数量
    size1 = '6390000'

    print("购买中")
    number = spotAPI.get_specific_ticker('SHIB-USDT')                                  #获取交易币种（SHIB-USDT）的信息

    price = float(number["last"]) - float(number["last"]) * 0.1                       #last为交易币种的最新市场价

    price = str('{:.8f}'.format(price))                                                #保留有效数字与交易所相符合

    # 购买货币
    result2 = spotAPI.take_order(instrument_id='SHIB-USDT', side='buy', client_oid='a1', type='limit', size=size,
                                 price=price, order_type='0', notional='')                                      #购买货币
    #result1为刚才成交的那笔订单信息
    result1 = spotAPI.get_order_info(instrument_id='SHIB-USDT', order_id=result2["order_id"], client_oid='')
    print(result1)
    print("购买完成")


    #以下为个人编写的量化交易核心算法

    n = 0
    while True:
        try:
            if result1["side"] == "buy":
                if result1["state"] == "0":
                    print("未购买完成")
                    if n == 3300:                          #n3300为一个周期，若始终挂单未交易成功则取消下单 后重新分析数据重新下单
                        print("取消下单")
                        result = spotAPI.revoke_order(instrument_id='SHIB-USDT', order_id=result2["order_id"],
                                                      client_oid='')
                        print("重新下单")
                        time.sleep(10)
                        number = spotAPI.get_specific_ticker('SHIB-USDT')
                        price = float(number["last"]) - float(number["last"]) * 0.1
                        price = str('{:.8f}'.format(price))

                        #result2为限价挂单 买
                        result2 = spotAPI.take_order(instrument_id='SHIB-USDT', side='buy', client_oid='a1',
                                                     type='limit',
                                                     size=size,
                                                     price=price, order_type='0', notional='')
                        n = 0
                elif result1["state"] == "2":
                    print("购买成功")
                    price2 = float(result1["price"]) + float(result1["price"]) * 0.1                   #根据result1中买时成交价 得到卖价

                    price2 = str('{:.8f}'.format(price2))

                    # result2为限价挂单 卖
                    result2 = spotAPI.take_order(instrument_id='SHIB-USDT', side='sell', client_oid='a1', type='limit',
                                                 size=size1,
                                                 price=price2, order_type='0', notional='')

                    print("购买result2" + str(result2))
                elif result1["state"] == "-1":                                    #购买失败情况
                    print("购买取消")
                    break
                else:
                    print("购买出错，请检测result1" + str(result1))
            elif result1["side"] == "sell":
                if result1["state"] == "0":
                    print("未出售完成")
                elif result1["state"] == "2":
                    print("出售成功")
                    time.sleep(30)

                    number = spotAPI.get_specific_ticker('SHIB-USDT')
                    price = float(number["last"]) - float(number["last"]) * 0.1                #获得下次买价
                    price = str('{:.8f}'.format(price))

                    result2 = spotAPI.take_order(instrument_id='SHIB-USDT', side='buy', client_oid='a1', type='limit',
                                                 size=size,
                                                 price=price, order_type='0', notional='')
                    n = 0
                    print("售出result2" + str(result2))
                else:
                    print("出售出错，请检测result1" + str(result1))
                    break
            result1 = spotAPI.get_order_info(instrument_id='SHIB-USDT', order_id=result2["order_id"], client_oid='')      #得到交易信息
            time.sleep(1)
            n += 1
        except:
            print("出错，查看错误")
            print("result2" + str(result2))
            print("result1" + str(result1))

    print(time1 + json.dumps(result))                    #将python对象转换成json对象 打印

