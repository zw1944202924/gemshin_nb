
import request from '@/utils/request'

// 获取股票列表
export function getStockList(params) {
  return request({
    url: '/stock/list',
    method: 'get',
    params
  })
}
