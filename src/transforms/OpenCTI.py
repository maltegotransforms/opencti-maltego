# -*- coding: utf-8 -*-

# import the relevant objects from the maltego_trx library and locally added entities
#from maltego_trx.entities import *
from transforms.entities import *
from maltego_trx.maltego import UIM_PARTIAL
from maltego_trx.transform import DiscoverableTransform
from transforms.config import *
from pycti import OpenCTIApiClient

# 
class CampaignToAttackPatterns(DiscoverableTransform): 
    @classmethod
    def create_entities(cls, request, response):
        """
        Processes the Maltego request and returns the formatted data requested
        """
        opencti_api_client = OpenCTIApiClient(opencti["url"], opencti["token"], "error", False)

        search_term = request.Value

        try:
            hits = None # execute the scrape function and save the results
            if hits:
                # iterate through the hits dictionary and create an entity for each result
                for website_title, website_url in hits.items():
                    response.addEntity(Website, "%s:%s" % (website_title, website_url) )
            else:
                # send a message back to the Maltego user interface so the user knows there were no results
                response.addUIMessage("The provided search term did not result in any hits")
        except Exception as e:
            # send a message to the Maltego user interface with error information
            response.addUIMessage("An error occurred performing the search query: %s" % (e), messageType=UIM_PARTIAL)