import request from '@/utils/request'

export function getPortfolioList(params) {
  return request({
    url: '/api/portfolio/',
    method: 'get',
    params
  })
}

export function getPortfolioDetail(id) {
  return request({
    url: `/api/portfolio/${id}`,
    method: 'get'
  })
}

export function createPortfolio(data) {
  return request({
    url: '/api/portfolio/',
    method: 'post',
    data
  })
}

export function updatePortfolio(id, data) {
  return request({
    url: `/api/portfolio/${id}`,
    method: 'put',
    data
  })
}

export function deletePortfolio(id) {
  return request({
    url: `/api/portfolio/${id}`,
    method: 'delete'
  })
}

export function getPortfolioAnalysis(id) {
  return request({
    url: `/api/portfolio/${id}/analysis`,
    method: 'get'
  })
}