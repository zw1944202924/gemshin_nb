import request from '@/utils/request'

export function getWatchlist(params) {
  return request({
    url: '/watchlist/list',
    method: 'get',
    params
  })
}

export function addToWatchlist(data) {
  return request({
    url: '/watchlist/add',
    method: 'post',
    params: data
  })
}

export function removeFromWatchlist(data) {
  return request({
    url: `/watchlist/delete/${data.watchlist_id}`,
    method: 'delete',
    params: { user_id: data.user_id }
  })
}