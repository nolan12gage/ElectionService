
from database import *

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_restful import reqparse, abort, Resource, Api
import os, re, sys
import json, random
import requests
import xmltodict

application = Flask(__name__)
api = Api(application)

base_port = 6000

participants = int(sys.argv[1])
participant_id = int(sys.argv[2])

vote_type = ''
if len(sys.argv) < 4:
	vote_type = 'r'
else:
	vote_type = sys.argv[3]

port_num = base_port + participant_id

parser = reqparse.RequestParser()
parser.add_argument('election')
parser.add_argument('winner')

# Initiate
# Used to initiate an election
# Calls: Coordinator.InitiatorVote and Participant.Vote
class Initiate(Resource):
  def post(self):
	
		# Parse arguments
    args = parser.parse_args()

		# Cast vote - type 's' indicates a selfish vote, otherwise is random
    if vote_type == 's':
      vote = participant_id
    else:
      vote = random.randint(1, participants)

		# Build endpoint and arguments to call Coordinator.InitiatorVote
    ivote_ep = 'http://127.0.0.1:5000/coordinator/initiatorVote'
    election = args['election']
    payload = { 'election': election, 'participants': participants, 'vote': vote }
    placeholder = requests.post(ivote_ep, params=payload)
		
    print('Election #' + election + ': with vote for service ' + str(vote))
		
		# Invoke the other participant services to vote
    payload_2 = { 'election': election }
    for i in range (1, participants+1):
      if i != participant_id:
        vote_ep = 'http://127.0.0.1:' + str(base_port + i) + '/participant/vote'
        requests.post(vote_ep, params=payload_2)
		
    return 200
		
# Vote
# Used to tell a service to cast a vote
# Calls: Coordinator.ParticipantVote
class Vote(Resource):
	def post(self):
	
		# Parse the arguments
		args = parser.parse_args()

		# Cast vote - type 's' indicates a selfish vote, otherwise is random
		if vote_type == 's':
			vote = participant_id
		else:
			vote = random.randint(1, participants)
		
		# Build endpoint and arguments to call Coordinator.ParticipantVote
		pvote_ep = 'http://127.0.0.1:5000/coordinator/participantVote'
		election = args['election']
		payload = { 'election': election, 'vote': vote }
		
		print('Election #' + election + ': Voting for service ' + str(vote))		
		requests.post(pvote_ep, params=payload)		
		
		return 200
		
# Results
# Sends the result of an election to all of the 
class Results(Resource):
	def post(self):
	
		# Parse the arguments
		args = parser.parse_args()
	
		# Print the election and winner to the console output
		election = args['election']
		winner = args['winner']
		print('Election #' + election + ': Service ' + str(winner) + ' won!')
		
		return 200
				
##
## Actually setup the Api resource routing here
##
api.add_resource(Initiate, '/participant/initiate')
api.add_resource(Vote, '/participant/vote')
api.add_resource(Results, '/participant/results')

		
if __name__ == "__main__":
    application.run(port=port_num, debug=True, threaded=True)
	








	