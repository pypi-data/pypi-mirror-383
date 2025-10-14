

<font style="color:#DF2A3F;">注：</font>

<font style="color:#DF2A3F;">1、标黄为终态，推送该状态后续不会在继续推送内容</font>

<font style="color:#DF2A3F;">2、付费用户以此状态为准，不使用 state</font>

| <font style="color:#ffffff;">物流状态</font> | | <font style="color:#ffffff;">状态码</font> | <font style="color:#ffffff;">业务字段说明</font> |
| :--- | --- | :--- | :--- |
| <font style="color:#000000;">已揽收</font> | <font style="color:#000000;">已揽收</font> | <font style="color:#000000;">1</font> | <font style="color:#000000;">快递员已上门揽收快递</font> |
| | <font style="color:#000000;">待揽件</font> | <font style="color:#000000;">10</font> | <font style="color:#000000;">快递员未去取件</font> |
| <font style="color:#000000;">在途中</font> | <font style="color:#000000;">到达派件城市</font> | <font style="color:#000000;">201</font> | <font style="color:#000000;">快件到达派件城市</font> |
| | <font style="color:#000000;">派件中</font> | <font style="color:#000000;">202</font> | <font style="color:#000000;">快件由派件员进行派件</font> |
| | <font style="color:#000000;">已放入快递柜或驿站</font> | <font style="color:#000000;">211</font> | <font style="color:#000000;">快件放入快递柜或者驿站</font> |
| | <font style="color:#000000;">到达转运中心</font> | <font style="color:#000000;">204</font> | <font style="color:#000000;">快件在转运中心做到件扫描</font> |
| | <font style="color:#000000;">到达派件网点</font> | <font style="color:#000000;">205</font> | <font style="color:#000000;">快件在派件网点做到件扫描</font> |
| | <font style="color:#000000;">寄件网点发件</font> | <font style="color:#000000;">206</font> | <font style="color:#000000;">快件在寄件网点做发件扫描</font> |
| | <font style="color:#000000;">在途</font> | <font style="color:#000000;">2</font> | <font style="color:#000000;">货物在途中运输</font> |
| <font style="color:#000000;">已签收</font> | <font style="color:#000000;">正常签收</font> | <font style="color:#000000;">301</font> | <font style="color:#000000;">快件由收件人签收</font> |
| | <font style="color:#000000;">异常后最终签收</font> | <font style="color:#000000;">302</font> | <font style="color:#000000;">快件途中出现异常后，正常签收</font> |
| | <font style="color:#000000;">代收签收</font> | <font style="color:#000000;">304</font> | <font style="color:#000000;">快件由非收件人本人代签</font> |
| | <font style="color:#000000;">快递柜或驿站签收</font> | <font style="color:#000000;">311</font> | <font style="color:#000000;">快件由快递柜或驿站签收</font> |
| | <font style="color:#000000;">已签收</font> | <font style="color:#000000;">3</font> | <font style="color:#000000;">快件被签收</font> |
| <font style="color:#000000;">转寄</font> | <font style="color:#000000;">转寄</font> | <font style="color:#000000;">5</font> | <font style="color:#000000;">快递被转寄到新地址</font> |
| <font style="color:#000000;">问题件</font> | <font style="color:#000000;">发货无信息</font> | <font style="color:#000000;">401</font> | <font style="color:#000000;">运单轨迹中没有任何描述，或者直接为空，</font><font style="color:#000000;">   </font><font style="color:#000000;">或者描述上发货无信息</font> |
| | <font style="color:#000000;">超时未签收</font> | <font style="color:#000000;">402</font> | <font style="color:#000000;">运单最后一条轨迹(含有派件动作的描述)，该条轨迹产生时间，距当前查询时间，超时36 小时或轨迹中描述超时未签收</font> |
| | <font style="color:#000000;">超时未更新</font> | <font style="color:#000000;">403</font> | <font style="color:#000000;">运单轨迹最后一条时间距当前时间超过5天</font> |
| | <font style="color:#000000;">拒收（退件）</font> | <font style="color:#000000;">404</font> | <font style="color:#000000;">客户拒收产生退件</font> |
| | <font style="color:#000000;">派件异常</font> | <font style="color:#000000;">405</font> | <font style="color:#000000;">派件异常</font> |
| | <font style="color:#000000;">退货签收</font> | <font style="color:#000000;">406</font> | <font style="color:#000000;">退件后由寄件人进行签收</font> |
| | <font style="color:#000000;">退货未签收</font> | <font style="color:#000000;">407</font> | <font style="color:#000000;">退件后由寄件人未签收</font> |
| | <font style="color:#000000;">快递柜或驿站超时未取</font> | <font style="color:#000000;">412</font> | <font style="color:#000000;">放入快递柜后超过18个小时没有取件</font> |
| | <font style="color:#000000;">单号已拦截</font> | <font style="color:#000000;">413</font> | <font style="color:#000000;">快件在途中被快递员拦截</font> |
| | <font style="color:#000000;">破损</font> | <font style="color:#000000;">414</font> | <font style="color:#000000;">货物破损</font> |
| | <font style="color:#000000;">客户取消发货</font> | <font style="color:#000000;">415</font> | <font style="color:#000000;">客户取消下单</font> |
| | <font style="color:#000000;">无法联系</font> | <font style="color:#000000;">416</font> | <font style="color:#000000;">派送中无法联系到收件人</font> |
| | <font style="color:#000000;">配送延迟</font> | <font style="color:#000000;">417</font> | <font style="color:#000000;">快递公司配送延迟</font> |
| | <font style="color:#000000;">快件取出</font> | <font style="color:#000000;">418</font> | <font style="color:#000000;">快递员把快件从快递柜取出</font> |
| | <font style="color:#000000;">重新派送</font> | <font style="color:#000000;">419</font> | <font style="color:#000000;">快递员与客户沟通 重新派送</font> |
| | <font style="color:#000000;">收货地址不详细</font> | <font style="color:#000000;">420</font> | <font style="color:#000000;">收货地址不详细</font> |
| | <font style="color:#000000;">收件人电话错误</font> | <font style="color:#000000;">421</font> | <font style="color:#000000;">收件人电话错误</font> |
| | <font style="color:#000000;">错分件</font> | <font style="color:#000000;">422</font> | <font style="color:#000000;">网点或中心错误分拣</font> |
| | <font style="color:#000000;">超区件</font> | <font style="color:#000000;">423</font> | <font style="color:#000000;">派件超出派送范围</font> |
| | <font style="color:#000000;">问题件</font> | <font style="color:#000000;">4</font> | <font style="color:#000000;">问题件</font> |
| <font style="color:#000000;">清关</font> | <font style="color:#000000;">清关</font> | <font style="color:#000000;">6</font> | <font style="color:#000000;">货物在目的国清关</font> |
| | <font style="color:#000000;">待清关</font> | <font style="color:#000000;">601</font> | <font style="color:#000000;">货物在目的国待清关</font> |
| | <font style="color:#000000;">清关中</font> | <font style="color:#000000;">602</font> | <font style="color:#000000;">货物在目的国清关</font> |
| | <font style="color:#000000;">已清关</font> | <font style="color:#000000;">603</font> | <font style="color:#000000;">货物在目的国已清关</font> |
| | <font style="color:#000000;">清关异常</font> | <font style="color:#000000;">604</font> | <font style="color:#000000;">货物在目的国出现清关异常</font> |
| <font style="color:#000000;">暂无轨迹信息</font> | <font style="color:#000000;">暂无轨迹信息</font> | <font style="color:#000000;">0</font> | <font style="color:#000000;">货物暂无轨迹信息</font> |


