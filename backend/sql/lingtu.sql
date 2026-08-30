-- ============================================================
-- 说明: lingtu 库完整导出(结构 + 当前数据),可直接在 MySQL/DataGrip 中执行。
-- 对应模型: backend/app/models/user.py (SQLAlchemy)
-- ============================================================

CREATE DATABASE IF NOT EXISTS `lingtu` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `lingtu`;

-- ------------------------------------------------------------
-- 用户表 users
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id`            int NOT NULL AUTO_INCREMENT COMMENT '主键',
    `username`      varchar(32)  NOT NULL COMMENT '用户名(唯一)',
    `password_hash` varchar(255) NOT NULL COMMENT '密码哈希(Argon2)',
    `role`          enum('USER','ADMIN') NOT NULL DEFAULT 'USER' COMMENT '角色',
    `status`        enum('ACTIVE','DISABLED') NOT NULL DEFAULT 'ACTIVE' COMMENT '账号状态',
    `created_at`    datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
    `updated_at`    datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `ix_users_username` (`username`)
) ENGINE = InnoDB AUTO_INCREMENT = 5 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表';

-- ------------------------------------------------------------
-- 当前数据 (4 条: 1 个管理员 + 3 个普通用户)
-- 密码哈希为 Argon2id;admin 明文密码为 admin12345,其余为注册时设置
-- ------------------------------------------------------------
INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `status`, `created_at`, `updated_at`) VALUES (1,'admin','$argon2id$v=19$m=65536,t=3,p=4$FSqm0Y/egxKy+f5iYQdrsQ$gQigNXMxu9eq2jICDThKxQAsH5Eporc6yiVGxhGk7gA','ADMIN','ACTIVE','2026-08-29 21:47:33','2026-08-29 21:47:33');
INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `status`, `created_at`, `updated_at`) VALUES (2,'xiaoming2024','$argon2id$v=19$m=65536,t=3,p=4$eDYe4za4h61zV4dZRDm8LQ$o+pqUyN+dVu9nNHEsJlPhKlBswocw0SCVCKUmfFMTVw','USER','ACTIVE','2026-08-29 21:48:56','2026-08-29 21:48:56');
INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `status`, `created_at`, `updated_at`) VALUES (3,'guitester01','$argon2id$v=19$m=65536,t=3,p=4$R+jxcDOnH/Bz1zXnPExG7g$nR0R3PFm3U0bP54MLqmz4IMI3Xekn4Wrxv03X147b10','USER','ACTIVE','2026-08-29 21:58:45','2026-08-29 21:58:45');
INSERT INTO `users` (`id`, `username`, `password_hash`, `role`, `status`, `created_at`, `updated_at`) VALUES (4,'sunbai','$argon2id$v=19$m=65536,t=3,p=4$e6+Kl8KUbSFYHSvdToVN7g$fEnV2i+6UrTy+tb6MCJkDxFkht86AGIo6Gcf5SZHx7Q','USER','ACTIVE','2026-08-30 00:11:10','2026-08-30 00:11:10');
