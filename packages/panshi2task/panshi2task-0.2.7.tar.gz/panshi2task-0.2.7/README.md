# proto相关代码生成
proto文件来自于多个panshi-task-*项目
windows下,运行codegen.bat

# 登录
poetry config http-basic.dplus admin numgal.nexus.admin

# 打包及推送
poetry build
poetry publish --repository dplus