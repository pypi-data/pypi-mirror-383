# panshi-file-parser

文件解析服务，包含解析、切分，支持pdf、word、markdown、txt、html等文件类型

pfip   panshi_file_inlli_processor

# 打包发布

```shell
poetry config http-basic.dplus admin numgal.nexus.admin
poetry config repositories.dplus http://192.168.3.3:8081/repository/pypi-hosted/
poetry publish --build --repository dplus 
poetry cache clear dplus --all
```