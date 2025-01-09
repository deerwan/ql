/**
 * Rabbit更换server脚本
 * 环境变量
 * export rabbitname=""
 * export rabbitpwd=""
 * export rabbiturl=""
 * 烟雨阁仿照九佬改写青龙版 
 */



const axios = require("axios").default;

const Notify = 1; 		// 0为关闭通知, 1为打开通知, 默认为1
const debug = 0;			// 0为关闭调试, 1为打开调试, 默认为0

// 获取环境变量
let username = process.env.rabbitname || '';   // 从环境变量获取用户名
let password = process.env.rabbitpwd || '';   // 从环境变量获取密码
let url = process.env.rabbiturl || '';         // 从环境变量获取url

const notify = require("./sendNotify");  // 发送通知模块

// 发送通知消息
async function SendMsg(message) {
    if (!message) return;
    if (Notify > 0) {
        await notify.sendNotify("Rabbit更换server脚本", message);  // 发送通知
    } else {
        console.log(message);  // 如果没有开启通知，直接打印消息
    }
}

// 用于聚合消息
let aggregatedMessage = "";

// 在合适的地方收集信息
async function fetchData() {
    try {
        // 登录请求
        const adminResponse = await axios.post(`${url}/admin/auth`, {
            username: username,
            password: password
        }, {
            headers: {
                Accept: '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': 'PostmanRuntime-ApipostRuntime/1.1.0',
                Connection: 'keep-alive',
                'Content-Type': 'application/json'
            }
        });

        // 登录失败时处理
        if (adminResponse.data.code === 401) {
            console.error('登录失败：账号或密码错误');
            aggregatedMessage += '登录失败：账号或密码错误\n'; // 聚合消息
            return;  // 退出函数
        }

        // 获取token
        const token = adminResponse.data.access_token;

        // 获取配置请求
        const peizResponse = await axios.post(`${url}/admin/GetConfig`, {}, {
            headers: {
                Authorization: 'Bearer ' + token,
                Accept: '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': 'PostmanRuntime-ApipostRuntime/1.1.0',
                Connection: 'keep-alive'
            }
        });

        // 获取失败时处理
        if (peizResponse.data.code === 422) {
            console.error('获取配置失败：Invalid header padding');
            aggregatedMessage += '获取配置失败：看看是不是你配置有问题\n'; // 聚合消息
            return;  // 退出函数
        }

        // 打印配置
        const serverHost = peizResponse.data.ServerHost;
        console.log('当前ServerHost:', serverHost);
        aggregatedMessage += `当前ServerHost: ${serverHost}\n`; // 聚合消息

        // host列表
        const hostlist = [
            "mr-orgin.1888866.xyz",
            "jd-orgin.1888866.xyz",
            "mr.118918.xyz",
            "host.257999.xyz",
            "fd.gp.mba:6379"
        ];

        // 随机选择一个host
        const selectedHost = hostlist[Math.floor(Math.random() * hostlist.length)];

        // 更新ServerHost
        const host = await axios.post(`${url}/admin/SaveConfig`, {
            ServerHost: selectedHost // 随机选择一个host
        }, {
            headers: {
                Authorization: 'Bearer ' + token,
                Accept: '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': 'PostmanRuntime-ApipostRuntime/1.1.0',
                Connection: 'keep-alive'
            }
        });

        // 更新失败时处理
        if (host.data.code === 422) {
            console.error('更新配置失败：Signature verification failed');
            aggregatedMessage += '更新配置失败：看看配置是不是错了\n'; // 聚合消息
            return;  // 退出函数
        }

        // 打印更新后的配置
        console.log('更新后ServerHost:', host.data.msg, "-----", selectedHost);
        aggregatedMessage += `更新后ServerHost: ${host.data.msg} ----- ${selectedHost}\n`; // 聚合消息

    } catch (error) {
        console.error('发生错误:', error);
        aggregatedMessage += `发生错误: ${error.message}\n`; // 聚合消息
    }

    // 最后一次性发送消息
    await SendMsg(aggregatedMessage);
}

// 调用异步函数
fetchData();
