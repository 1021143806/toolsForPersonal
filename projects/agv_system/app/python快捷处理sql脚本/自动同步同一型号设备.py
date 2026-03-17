#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本功能：
1. 连接源数据库（10.68.2.32），查询所有 DEVICETYPE = 'RTA-C060-Q-2L-410' 的记录。
2. 对于每条记录，去除 ID 字段后，生成 INSERT 语句并执行到目标数据库（10.68.2.40）。
3. 使用 INSERT IGNORE 避免因主键或唯一键冲突而报错，冲突时自动跳过。
4. 输出插入成功与跳过的记录数。
"""

import pymysql

# ========== 配置数据库连接信息 ==========
# 源数据库（10.68.2.32）
SOURCE_DB_CONFIG = {
    'host': '10.68.2.27',
    'port': 3306,
    'user': 'wms',                # 请根据实际情况修改
    'password': 'CCshenda889',     # 请根据实际情况修改
    'database': 'wms',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor   # 返回字典格式，便于字段操作
}

# 目标数据库（10.68.2.40）
TARGET_DB_CONFIG = {
    'host': '10.68.2.40',
    'port': 3306,
    'user': 'wms',
    'password': 'CCshenda889',
    'database': 'wms',
    'charset': 'utf8mb4'
}

# 目标表名
TABLE_NAME = 'agv_robot'

# 目标表字段列表（除去 ID 后的顺序，必须与表结构一致）
TARGET_FIELDS = [
    'DEVICE_CODE', 'DEVICE_IP', 'DEVICE_PORT', 'USRENAME', 'PASSWORD',
    'DEVICETYPE', 'CAPACITIES', 'DETAILTYPE', 'MAC', 'UPDATE_DATE',
    'CREATE_DATE', 'config', 'CONFIG_PARM', 'VERSION_SN', 'PROTOCOL',
    'MACS_VERSION', 'MILEAGE', 'DIRECT_CONNECTION'
]

# 查询条件
DEVICE_TYPE = 'RTA-C060-Q-2L-410'


def main():
    source_conn = None
    target_conn = None
    try:
        # 1. 连接源数据库并查询数据
        print("正在连接源数据库...")
        source_conn = pymysql.connect(**SOURCE_DB_CONFIG)
        with source_conn.cursor() as cursor:
            sql = "SELECT * FROM agv_robot WHERE DEVICETYPE = %s"
            cursor.execute(sql, (DEVICE_TYPE,))
            rows = cursor.fetchall()
            print(f"从源库查询到 {len(rows)} 条记录。")

        if not rows:
            print("没有符合条件的数据，程序结束。")
            return

        # 2. 连接目标数据库
        print("正在连接目标数据库...")
        target_conn = pymysql.connect(**TARGET_DB_CONFIG)
        target_cursor = target_conn.cursor()

        # 3. 构造 INSERT IGNORE 语句（占位符方式）
        placeholders = ', '.join(['%s'] * len(TARGET_FIELDS))
        fields_str = ', '.join([f'`{f}`' for f in TARGET_FIELDS])
        insert_sql = f"INSERT IGNORE INTO `{TABLE_NAME}` ({fields_str}) VALUES ({placeholders})"

        success_count = 0
        skip_count = 0

        # 4. 逐条插入数据
        for row in rows:
            # 按 TARGET_FIELDS 顺序提取值，如果字段在 row 中不存在则设为 None
            values = [row.get(field) for field in TARGET_FIELDS]
            try:
                target_cursor.execute(insert_sql, values)
                if target_cursor.rowcount == 1:
                    success_count += 1
                else:
                    # rowcount = 0 表示被 IGNORE 忽略（重复键）
                    skip_count += 1
            except Exception as e:
                # 其他异常（如数据类型不匹配）回滚并计数为失败
                target_conn.rollback()
                print(f"插入失败，错误信息：{e}")
                print(f"问题数据：{values}")
                # 可根据需要选择是否终止脚本，这里继续下一条
                continue

        # 提交事务（实际上逐条执行时，execute 后不需要立即 commit，但为了保险可以批量 commit）
        target_conn.commit()

        print(f"\n操作完成！成功插入 {success_count} 条，跳过（重复） {skip_count} 条。")

    except Exception as e:
        print(f"脚本执行过程中出现错误：{e}")
    finally:
        # 关闭数据库连接
        if source_conn:
            source_conn.close()
        if target_conn:
            target_conn.close()


if __name__ == '__main__':
    main()