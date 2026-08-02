import { describe, expect, it } from "vitest"

import { getAuditDetailRows, getAuditResultLabel, getAuditSummary } from "../utils/auditLog"

describe("auditLog utils", () => {
  it("should format readable detail rows", () => {
    const rows = getAuditDetailRows({
      detail: {
        old_roles: ["游客"],
        new_roles: ["AI 股票投资者"],
        fields: ["display_name", "email"],
        must_change_password: true
      }
    })

    expect(rows).toEqual([
      "修改字段：显示名称、邮箱",
      "原角色：游客",
      "新角色：AI 股票投资者",
      "下次登录需改密：是"
    ])
  })

  it("should hide sensitive detail keys", () => {
    const rows = getAuditDetailRows({
      detail: {
        password_hash: "abc",
        new_password: "plaintext",
        credential_token: "secret-token",
        roles: ["管理员"]
      }
    })

    expect(rows).toEqual(["分配角色：管理员"])
  })

  it("should use provided summary and result label", () => {
    expect(getAuditSummary({ summary: "管理员 zhangwei 重置了 ordinary_user 的密码" })).toBe(
      "管理员 zhangwei 重置了 ordinary_user 的密码"
    )
    expect(getAuditResultLabel("success")).toBe("成功")
    expect(getAuditResultLabel("failed")).toBe("失败")
  })
})
