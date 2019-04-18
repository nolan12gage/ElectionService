
from database import *

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_restful import reqparse, abort, Resource, Api
import os, re, sys
import json, random
import requests
import xmltodict

application = Flask(__name__)
api = Api(application)

election = 10001
base_port = 6000
elections_dict = {}

#def abort_if_endpoint_doesnt_exist(todo_id):
#  if todo_id not in ENDPOINTS:
#    abort(404, message="Endpoint {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('election')
parser.add_argument('vote')
parser.add_argument('participants')


# Election - Called by front end when a new election is started
# Calls Participant.Initiate
class Election(Resource):
  def post(self):
	
		# The first service will always be the initiator.  This way we can run with any #
		# of services > 0 if they are initialized in number order (starting at 1)
    initiator = 1    
    initiator_ep = 'http://127.0.0.1:' + str(base_port + initiator) + '/participant/initiate'
		
		# Set up the request params
    global election
    payload = {'election': election}

		# Submit the POST request for Participant.Initiate, then increment the election
    print('Election #' + str(election) + ': Created')
    requests.post(initiator_ep, params=payload)
    election += 1
		
    return payload

		
# InitiatorVote - Called by participant when they cast a vote
# Returns
class InitiatorVote(Resource):
	def post(self):
		
		# Parse and store arguments
		args = parser.parse_args()
		election_for_vote = int(args['election'])
		participants = int(args['participants'])
		vote = int(args['vote'])
		
		# Set up structure for keeping track of votes for this election
		election_votes = {}
		for i in range (1, participants+1):
			election_votes[i] = 0
		elections_dict[election_for_vote] = election_votes
		
		# Count vote
		elections_dict[election_for_vote][vote] += 1
		print('Election #' + str(election_for_vote) + ': Vote received for service ' + str(vote))
		
		# Determine winner and whether everyone has voted
		# Tiebreaker will be lowest participant_id
		votes_cast = 0
		winner = 0
		highest_vote_count = 0
		
		for service in elections_dict[election_for_vote]:
			votes_cast += elections_dict[election_for_vote][service]
			if elections_dict[election_for_vote][service] > highest_vote_count:
				highest_vote_count = elections_dict[election_for_vote][service]
				winner = service
				
		# If election is done, announce the winner
		if votes_cast == participants:
			#print(elections_dict)
			print('Election #' + str(election_for_vote) + ': Announcing winner')
			for i in range (1, participants+1):
				results_ep = 'http://127.0.0.1:' + str(base_port + i) + '/participant/results'
				payload = {'election': election_for_vote, 'winner': winner}
				requests.post(results_ep, params=payload)
		
		return 200
		
		
# ParticipantVote - Called by participant when they cast a vote
# Returns
class ParticipantVote(Resource):
	def post(self):
	
		# Parse and store arguments
		args = parser.parse_args()
		election_for_vote = int(args['election'])
		vote = int(args['vote'])

 		# Count vote
		elections_dict[election_for_vote][vote] += 1
		print('Election #' + str(election_for_vote) + ': Vote received for service ' + str(vote))

		# Get total number of participants for vote
		participants = len(elections_dict[election_for_vote])
		
		# Determine winner and whether everyone has voted
		# Tiebreaker will be lowest participant_id
		votes_cast = 0
		winner = 0
		highest_vote_count = 0
		
		for service in elections_dict[election_for_vote]:
			votes_cast += elections_dict[election_for_vote][service]
			if elections_dict[election_for_vote][service] > highest_vote_count:
				highest_vote_count = elections_dict[election_for_vote][service]
				winner = service
				
		# If election is done, announce the winner
		if votes_cast == participants:
			#print(elections_dict)
			print('Election #' + str(election_for_vote) + ': Announcing winner')
			for i in range (1, participants+1):
				results_ep = 'http://127.0.0.1:' + str(base_port + i) + '/participant/results'
				payload = {'election': election_for_vote, 'winner': winner}
				requests.post(results_ep, params=payload)
		
		return 200 
		
class ViewResults(Resource):
	def get(self):
		return elections_dict
##
## Actually setup the Api resource routing here
##
api.add_resource(Election, '/coordinator/election')
api.add_resource(ParticipantVote, '/coordinator/participantVote')
api.add_resource(InitiatorVote, '/coordinator/initiatorVote')
api.add_resource(ViewResults, '/coordinator/viewResults')



		
if __name__ == "__main__":
    application.run(port=5000, debug=True, threaded=True)
	








	