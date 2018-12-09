# Bit Bucket top commit #

*   Accessing the Bitbucket api v2.0.
*   Get the list of repo with uuid.
*   Get the history of commit with author with the limit.
*   Sort and get the top commiter.
*   List the number of commits per repository and total percentage share of commits for each author in json format.

* Version - 1.0

### How do I get set up? ###

* Clone the repo
* install python 3.5 and above
* Dependencies package - requests, json, operator

### How to run the python script ###

* chmod +x bitBucketTopCommit.py
* ./bitBucketTopCommit.py <team_name> <top> <limit>

or

* python 3.6 bitBucketTopCommit.py <team_name> <top> <limit>

~~~~
     team_name -> team name of bit bucket 
     top -> display names of at most TOP committers taking into account all git repositories of the team 
     limit -> at most LIMIT latest commits per repository.
~~~~

* ex: ./bitBucketTopCommit.py devops_team_x 3 1

* output:
~~~~
            {
              "devops_team_x": {
                "Ahamed Yaser Arafath <ahamedyaserarafath@gmail.com>": {
                  "git_repos": {
                    "testing1": "1",
                    "testing2_repo": "1"
                  },
                  "total_commit_share_percentage": 100.0
                }
              }
            }
~~~~
