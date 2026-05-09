# 普通用户个人档案轻量拆分设计

日期：2026-05-07

## 执行边界

- 本阶段只产出设计，不新增迁移脚本。
- 管理员账号继续只表达 **账户信息**，不进入普通用户档案体系。
- 不新增 `user_diagnosis_feedback` 表；`diagnosis` 留在 `user_profiles`，继续表达 **诊断反馈**。

## 目标结构

### `users`

普通用户账户信息：

- `id`
- `username`
- `email`
- `password_hash`
- `created_at`

### `admin_users`

管理员账户信息：

- `id`
- `username`
- `email`
- `password_hash`
- `created_at`

不关联 `user_profiles`、`user_risk_factor_profiles`、`bp_records`、`prediction_records`。

### `user_profiles`

普通用户个人档案主表：

- `id`
- `user_id`
- `nickname`
- `avatar`
- `diagnosis`
- `updated_at`

`diagnosis` 只表示用户提供的 **诊断反馈**：

- 可用于训练数据导出标签来源。
- 可用于个人中心反馈展示。
- 不进入用户侧 **双模型预测引擎** 的核心风险输入。

### `user_risk_factor_profiles`

普通用户风险因素档案：

- `id`
- `user_id`
- `age`
- `male`
- `height`
- `weight`
- `current_smoker`
- `cigs_per_day`
- `bp_meds`
- `diabetes`
- `tot_chol`
- `glucose`
- `updated_at`

该表是用户侧 **7 天风险预测** 的个人风险因素来源。BMI 继续由 `height/weight` 计算，不落库。

## 迁移步骤草案

1. 创建 `user_risk_factor_profiles`。
2. 从当前 `user_profiles` 回填风险因素字段：
   - `user_id`
   - `age`
   - `male`
   - `height`
   - `weight`
   - `current_smoker`
   - `cigs_per_day`
   - `bp_meds`
   - `diabetes`
   - `tot_chol`
   - `glucose`
   - `updated_at`
3. 保留 `user_profiles.nickname/avatar/diagnosis/updated_at`。
4. 删除 `user_profiles` 中已迁移的风险因素列。
5. 为 `user_risk_factor_profiles.user_id` 建唯一索引。

## Downgrade 回滚草案

1. 在 `user_profiles` 中恢复风险因素列。
2. 从 `user_risk_factor_profiles` 回填原列。
3. 删除 `user_risk_factor_profiles`。
4. 保留 `diagnosis` 在 `user_profiles` 中。

## 后端兼容过渡

第一阶段代码兼容：

- `User.profile` 继续指向 `user_profiles`。
- 新增 `User.risk_factor_profile` 指向 `user_risk_factor_profiles`。
- `User.to_dict()` 合并账户信息、个人档案主信息和风险因素档案，保持前端已有字段输出。
- `ProfileService.update_profile()` 将展示资料/诊断反馈写入 `user_profiles`，将风险因素字段写入 `user_risk_factor_profiles`。
- `ProfilePayloadNormalizer` 的字段别名和校验规则继续复用，避免前端协议同时变化。

预测链路：

- `PredictionInputSnapshot.from_user_and_latest_bp()` 改为读取 `user.risk_factor_profile`。
- `diagnosis` 不进入 `PredictionInputSnapshot`。
- 若风险因素档案缺失，保持现有默认值策略和错误语义。

训练数据导出：

- 导出样本投影同时读取 `user_profiles.diagnosis` 与 `user_risk_factor_profiles`。
- `diagnosis` 继续作为训练标签来源之一。
- `TRAINING_EXPORT_COLUMNS` 不变。

管理员用户管理：

- `AdminUser.to_dict()` 不再伪造 `age`、`bmi`、`profile_complete`。
- 前端用户管理页将普通用户健康字段展示限定在普通用户行；管理员行只展示账号字段和角色。

## 前端兼容过渡

- `RawProfile` 和 `Profile` 暂时保留扁平字段，继续消费后端合并 DTO。
- ProfileForm 内部分为三个 payload：
  - 账户信息。
  - 风险因素档案。
  - 诊断反馈。
- 管理员用户表类型拆分普通用户行与管理员行，避免管理员行出现健康档案字段。

## 测试清单

后端：

- 迁移 upgrade 后，普通用户 `user_profiles` 与 `user_risk_factor_profiles` 数据完整。
- 迁移 downgrade 后，旧 `user_profiles` 风险因素列完整恢复。
- 个人中心读取和更新展示资料、诊断反馈、风险因素档案。
- 用户侧预测只读取风险因素档案，不读取诊断反馈。
- 训练数据导出使用诊断反馈作为标签来源，并使用风险因素档案作为模型特征来源。
- 管理员账号不创建 profile 或 risk factor profile。

前端：

- 个人中心三个 section 行为不变。
- 诊断反馈保存不污染风险因素保存 payload。
- 管理员用户表管理员行不显示年龄、BMI、档案完整度。

## 实施建议

- 该拆分属于 schema 变更，建议单独 PR/提交，不和查询优化混在一起。
- 先合并阶段 17-19 的查询优化，再实施此 schema 变更。
- 迁移前需要备份当前 `user_profiles`，并在预发库执行 upgrade/downgrade 演练。
