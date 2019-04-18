
from database import *

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from collections import OrderedDict
import os, re, sys
import json, random
import requests
import xmltodict

application = Flask(__name__)


@application.route('/startElection', methods=['GET', 'POST'])
def startElection():
	return render_template('start_election.html')
	

@application.route('/electionResults', methods=['GET', 'POST'])	
def electionResults():
	
	election_ep = 'http://127.0.0.1:5000/coordinator/viewResults'
	response = requests.get(election_ep)
	elections_json = response.json()
	elections_str = json.dumps(elections_json, sort_keys=True)
	elections_str = elections_str[1:-1]
	elections_str = elections_str.replace("},", "},,")
	elections_str = elections_str.replace('"', '')
	election_list = elections_str.split(",,")
	return render_template('election_results.html', election_list=election_list)

	
if __name__ == "__main__":
    application.run(port=8000, debug=True)
	








	