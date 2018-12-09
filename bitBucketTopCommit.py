#!/usr/bin/python
# Note : Above path should be changed if python location is changed
##**************************************************************
##
## BitBucket Top Commit Json for the particular team
##   1. Accessing the Bitbucket api v2.0.
##   2. Get the list of repo with uuid.
##   3. Get the history of commit with author with the limit.
##   4. Sort and get the top commiter.
##   5. List the number of commits per repository 
##              and total percentage share of commits for each author in json format.
## 
## V 1.0 / 22 Sept 2018 / Ahamed Yaser Arafath / ahamedyaserarafath@gmail.com
##
##**************************************************************

import requests
requests.packages.urllib3.disable_warnings()
import sys
import json
import operator

class bitBucketTopCommiter():

  def __init__(self,team,top,limit):
    try:
      self.baseURL = "https://api.bitbucket.org/2.0/"
      # self.team = "devops_team_x"
      self.team = team
      # self.top = int("3")
      self.top = int(top)
      # self.limit = int("100")
      self.limit = int(limit)
    except Exception as e:
      self.DoError(str(e))
    
  def DoError (self,Error) :
     sys.exit(Error)

  def myGet (self,uri,key = 0 ) :
    '''
    Generic Api GET 
    '''
    URL = self.baseURL + str(uri)
    try :
      r=requests.get(URL, verify=False , timeout=120)
    except requests.exceptions.Timeout as e:
      self.DoError("HTTP Timeout Error Accessing "+URL)
    except requests.exceptions.ConnectionError as e:
      self.DoError("HTTP Connection Error Accessing "+URL + " " + str(e))
    except requests.exceptions.Requestexception as e:
      self.DoError("HTTP Error Accessing "+URL )
    try:
      if r.raise_for_status():
         self.DoError("Cannot access "+URL+" httpcode "+r.status_code )
    except:
     self.DoError("HTTP Error Accessing "+URL+" "+r.reason )
    if key == 0 :
      return r.text
    else:
      rdict=json.loads(r.text)
      return rdict[key]


  def getBitBucketRepo(self):
    '''
    Return the dict repositories for the particular team with uuid
    ex: 
    https://api.bitbucket.org/2.0/repositories/devops_team_x/
    
    output:
    dict_of_repository = 
              {
                  "testing1": "%7B9f8efa85-2f38-428b-9f8f-26ed1fa502a7%7D",
                  "testing2_repo": "%7B838c6f78-a535-4c27-99f4-4363336f9fb9%7D,
                  "testing3_repo": "%7B55575a72-be87-4f0a-85cb-f5d99427ef25%7D"
                }

    '''
    try:
      dict_of_repository={}
      repo_uri = "repositories/" + self.team + "/"
      git_bitbucket_repo_value=self.myGet(repo_uri,"values")
      for value in git_bitbucket_repo_value:
        dict_of_repository[value["name"]] = value["uuid"].replace("{","%7B").replace("}","%7D")
      return(dict_of_repository)
    except Exception as e:
      self.DoError(str(e))

  def getRepoCommitList(self,repo_uuid):
    '''
    Return the dict of commit history with author
    ex: 
    https://api.bitbucket.org/2.0/repositories/devops_team_x/%7B9f8efa85-2f38-428b-9f8f-26ed1fa502a7%7D/commits
    
    output:
    dict_of_commit_author = 
                  {
                    "Gregory Margo <gmargo@yahoo.com>": 1,
                    "Noel Waldron <noel.waldron@gmail.com>": 1,
                    "Ramesh Chamalla <ramesh.chamalla@gmail.com>": 1,
                    "Deepak Arora <deepak.arora@milwaukeetool.com>": 2,
                    "Caitlin Cecic <ccecic@atlassian.com>": 10,
                  }
    
    Note: 
    As some of the commit doesnt have ["author"]["user"]["username"] so going with raw data

    Improvement needs to be done : Can avoid one api hit when limit_last_length is zero
    '''
    try:
      dict_of_commit_author={}
      base_limit = 10
      limit_base_ten = int(int(self.limit)/base_limit)
      limit_last_length = int(int(self.limit)%base_limit)
      git_commit_limit_boolean = True
      for temp_limit in range(limit_base_ten):
        repo_commit_uri = "repositories/" +  self.team  + "/" + repo_uuid + "/commits" \
                                        + "?page=" + str(temp_limit+1) + "&pagelen=" + str(base_limit)
        git_repo_commit_value=self.myGet(repo_commit_uri,"values")
        if len(git_repo_commit_value) == 0:
          git_commit_limit_boolean=False
          break
        for value in git_repo_commit_value:
          # dict_of_commit_author.append((value["author"]["user"]["username"]))
          author = value["author"]["raw"]
          if author in dict_of_commit_author:
            temp_count = dict_of_commit_author[author]
            temp_count = temp_count + 1
            dict_of_commit_author[author] = temp_count
          else:
            dict_of_commit_author[author] = 1

      if git_commit_limit_boolean:
        repo_commit_uri = "repositories/" +  self.team  + "/" + repo_uuid + "/commits" \
                                        + "?page=" + str(limit_base_ten+1) + "&pagelen=" + str(limit_last_length)
        git_repo_commit_value=self.myGet(repo_commit_uri,"values")
        for value in git_repo_commit_value:
          # dict_of_commit_author.append((value["author"]["user"]["username"]))
          author = value["author"]["raw"]
          if author in dict_of_commit_author:
            temp_count = dict_of_commit_author[author]
            temp_count = temp_count + 1
            dict_of_commit_author[author] = temp_count
          else:
            dict_of_commit_author[author] = 1
      return(dict_of_commit_author)
    except Exception as e:
      self.DoError(str(e))


  def getTopCommitList(self,dict_of_repository):
    '''
    Return the total commit of every author and commit per repo for every author with sorting
    ex:
    overall_commit_author_sort = ([
                  ('Mary Anthony <manthony@atlassian.com>', 39), 
                  ('Paul Pritchard <ppritcha1@gmail.com>', 21), 
                  ('first name last <manthony@bitbucket.org>', 12), 
                  ('Caitlin Cecic <ccecic@atlassian.com>', 10), 
                  ('Tom Kane <tkane@atlassian.com>', 5), 
                  ('Emma Paris <ccecic+42@atlassian.com>', 4), 
                  ('Mary Anthony <buser.bb@gmail.com>', 4)])
    repo_commit_author = {
                    "sourcetree-starter-c": {
                      "David Cook <dcook@atlassian.com>": 1,
                      "first name last <manthony@bitbucket.org>": 3,
                      "Mary Anthony <manthony@atlassian.com>": 1
                    },
                    "online-edit-starter": {
                      "Mary Anthony <manthony@atlassian.com>": 1
                    }
                }
    '''
    try:
      overall_commit_author = {}
      repo_commit_author = {}
      for repo_name, repo_uuid in dict_of_repository.items():
        dict_of_commit_author = self.getRepoCommitList(repo_uuid)
        repo_commit_author[repo_name] = dict_of_commit_author
        for author, commit_count in dict_of_commit_author.items():
          if author in overall_commit_author:
            temp_commit_count = overall_commit_author[author]
            temp_commit_count = temp_commit_count + commit_count
            overall_commit_author[author] = temp_commit_count
          else:
            overall_commit_author[author] = commit_count
      overall_commit_author_sort=sorted(overall_commit_author.items(), key=operator.itemgetter(1), reverse=True)
      return overall_commit_author_sort, repo_commit_author
    except Exception as e:
      self.DoError(str(e))


  def getTopCommitRepo(self,overall_commit_author_sort,repo_commit_author):
    '''
    return the number of commits per repository of the top commiter in the last given value limit
    ex:
    top_commit_json =
                {
                  "tutorials": {
                    "Mary Anthony <manthony@atlassian.com>": {
                      "total_commit_share_percentage" : 30.85,
                      "git_repos": {
                        "splitpractice": "2",
                        "commitpractice": "3",
                        "MarkdownDemo": "11",
                        "sourcetree-starter": "20",
                        "sourcetree-starter-c": "1",
                        "online-edit-starter": "1",
                        "sourcetree-starter-b": "1"
                      }
                    },
                    "Paul Pritchard <ppritcha1@gmail.com>": {
                      "total_commit_share_percentage" : 18.73,
                      "git_repos": {
                        "commitpractice": "21"
                      }
                    }
                  }
                }    
    '''
    try:
      top_commit_json={}
      top_commit_author_dict={}
      temp_total_count = 0
      if self.top > len(overall_commit_author_sort):
        self.top = len(overall_commit_author_sort)
      for temp_total_count_value in range(len(overall_commit_author_sort)):
        temp_total_count = temp_total_count + overall_commit_author_sort[temp_total_count_value][1]
      for value in range(self.top):
        top_commit_author = overall_commit_author_sort[value][0]
        top_commit_author_total = overall_commit_author_sort[value][1]
        # import pdb;pdb.set_trace()
        top_commit_author_total_percentage = float("{0:.2f}".format((float(top_commit_author_total)/float(temp_total_count))*100))
        git_repos_author = {}
        repo_json = {}
        for repo_name, commit_dict in repo_commit_author.items():
          if commit_dict.get(top_commit_author):
            repo_json[repo_name] = str(commit_dict.get(top_commit_author))
        git_repos_author["git_repos"] = repo_json
        git_repos_author["total_commit_share_percentage"]=top_commit_author_total_percentage
        top_commit_author_dict[top_commit_author]=git_repos_author
      top_commit_json[self.team]=top_commit_author_dict
      return top_commit_json
    except Exception as e:
      self.DoError(str(e))




if __name__ == "__main__":
    try:
      team = sys.argv[1]
      top = sys.argv[2]
      limit = sys.argv[3]
      git_bucket_top_commiter_object = bitBucketTopCommiter(team,top,limit)
      dict_of_repository = git_bucket_top_commiter_object.getBitBucketRepo()
      overall_commit_author_sort,  repo_commit_author = git_bucket_top_commiter_object.getTopCommitList(dict_of_repository)
      result = git_bucket_top_commiter_object.getTopCommitRepo(overall_commit_author_sort,repo_commit_author)
      print(json.dumps(result, sort_keys=True, indent=2, separators=(',', ': ')))
    except Exception as e:
      print(str(e))

