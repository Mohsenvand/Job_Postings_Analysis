
import oauth2 as oauth
import libxml2
import sys

class JobPuller:


	jobKeywords = []
	def __init__(self, keyFile, job_search_keywords_file):
		# Create your consumer with the proper key/secret.
		keyFileReader = open(keyFile, 'r')
		lineCounter = 1
		apiKey = ""
		apiSecret = ""
		oauthKey = ""
		oauthSecret = ""
		for line in keyFileReader:
			if lineCounter == 1:
				lineParts = line.split('###')
				apiKey = lineParts[0]
				apiSecret = lineParts[1]
			if lineCounter == 2:
				lineParts = line.split('###')
				oauthKey = lineParts[0]
				oauthSecret = lineParts[1]
				break
			lineCounter = lineCounter + 1
				
		
		consumer = oauth.Consumer(apiKey, 
		    apiSecret)

		token = oauth.Token(
				oauthKey, 
				oauthSecret)

		# Create our client.
		self.client = oauth.Client(consumer, token)
		self.loadJobSearches(job_search_keywords_file)

	def loadJobSearches(self, job_keywords_file):
		fileReader = open(job_keywords_file, 'r')
		for line in fileReader:
			cleanedLine = line.strip('\n').strip()
			self.jobKeywords.append(cleanedLine)
		fileReader.close()			
	
	def collectSearches(self):
		request_url = "http://api.linkedin.com/v1/job-search"

		for keyword in self.jobKeywords:
			start = 0
			keyword = keyword.replace('&', '')
			fileName = keyword.replace(' ', '_').replace('/', '_')
			countryCode = 'us'
			count = 20
			initialRequest = request_url+"?keywords="+keyword+"&country-code="+countryCode+"&start="+str(start)+"&count="+str(count)
			response, initialContent = self.client.request(initialRequest)
			totalCount = self.parseTotalCount(initialContent)
			self.writeOutput(fileName, start, initialContent)
			start = start + count
			while(start<totalCount):
				nextRequest = request_url+"?keywords="+keyword+"&country-code="+countryCode+"&start="+str(start)+"&count="+str(count)
				response, content = self.client.request(nextRequest)
				self.writeOutput(fileName, start, content)
				start = start + count
				
	def writeOutput(self, fileName, start, content):
		outputWriter = open('postings/'+fileName+str(start), 'w+')
		outputWriter.write(content)
		outputWriter.close()
	
	def parseTotalCount(self, xmlContent):
		xmlDoc = libxml2.parseDoc(xmlContent)
		allTotals = xmlDoc.xpathEval("/job-search/jobs/@total")
		if len(allTotals) == 0:
			total = 0
		else:
			total = int(allTotals[0].content)
		print total
		return total
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "Please provide job keyword file"
		print "python JobPuller <path-to-key-file> <path-to-keyword-file>"
		exit(1)
	keyFile = str(sys.argv[1])
	keywordFile = str(sys.argv[2])
	puller = JobPuller(keyFile, keywordFile)
	puller.collectSearches()
