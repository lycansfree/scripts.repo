

## Download git client
```
https://git-for-windows.github.io/
https://git-scm.com/downloads
```

## Git global setup
```
git config --global user.name "YOUR_NAME"
git config --global user.email "YOUR_EMAIL"
git config --global core.autocrlf false
```

## Git的4步撤销

4个区的概念
- 工作区(Working Area)
- 暂存区(Stage)
- 本地仓库(Local Repository)
- 远程仓库(Remote Repository)

5种状态
- 未修改(Origin)
- 已修改(Modified)
- 已暂存(Staged)
- 已提交(Committed)
- 已推送(Pushed)

#### 检查修改状态
```
已修改，未暂存
git diff

已暂存，未提交
git diff --cached

已提交，未推送
git diff master origin/master
```
#### 撤销修改
```
已修改，未暂存
git checkout .  
或者  
git reset --hard

已暂存，未提交
git reset
git checkout .
或者
git reset --hard

已提交，未推送
git reset --hard origin/master

已推送
git reset --hard HEAD^ # 先恢复本地
git push -f # 再强制推送远程
```

## Git基本操作
```
clone仓库到本地: git clone http://gitlab.op.it.bx:8000/sample_group/sample_project.git
更新代码: git pull
查看文件的git状态: git status
创建分支: git branch <name>
切换分支: git checkout <name>
创建+切换分支: git checkout -b <name>
与主分支同步：git rebase origin/master
跟踪改动过的文件: git add . / git add <file>
代码提交到本地仓库: git commit -m "第一次提交"
查看变更内容: git diff
查看提交历史: git log
提交本地仓库的代码: git push origin <branch_name>
撤消工作目录中所有未提交文件的修改内容: git reset --hard HEAD
撤消指定的未提交文件的修改内容: git checkout HEAD <file>
撤消指定的提交: git revert <commit>
强制撤销本地未提交到远端的commit： 
git fetch --all 
git reset --hard origin/master
```

## Create a new repository
```
git clone http://gitlab.op.it.bx:8000/sample_group/sample_project.git
cd sample_project
touch README.md
git add README.md
git commit -m "add README"
git push -u origin master
```

## Add Existing folder as repository
```
cd existing_folder
git init
git remote add origin http://gitlab.op.it.bx:8000/sample_group/sample_project.git
git add .
git commit -m "Initial commit"
git push -u origin master
```

## Add ignore files which not want to managed by git
```
touch .gitignore
Add your ignore files or folder, such as
/.project
/.pydevproject
/.idea
```

## Work on branch
```
查看分支: git branch
创建分支: git branch <name>
切换分支: git checkout <name>
创建+切换分支: git checkout -b <name>
合并某分支到当前分支: git merge <name>

删除本地分支: git branch -d <name>
强行删除: git branch -D <name>

删除本地的远程分支：git branch -r -D origin/BranchName

删除git服务器上的分支：git push origin --delete BranchName
```

## Change your repository url
```
git remote set-url origin http://gitlab.qa.bx:8000/bxtools/itil.git
vi .git/config
change the url=http://gitlab.qa.bx:8000/bxtools/itil.git
```
