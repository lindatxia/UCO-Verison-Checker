## Team development notes 

### Branches 
- **master:** most stable & deployable working version of our project
- **develop:** changes in progress
- **feature-[whatever feature]:** branch off from develop, merge back into develop 

### Merging feature branches back to develop branches
`git checkout develop` <br />
`git merge --no-ff feature-name` <br />
`git branch -d feature-name` --> Deletes the feature branch once merged <br />
`git push origin develop` <br />