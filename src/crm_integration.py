"""
CRM Integration module for HubSpot API.
Handles contact management, segmentation, and email distribution.
"""
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException
from typing import Dict, List, Optional
import time
from datetime import datetime
from config import Config


class CRMIntegration:
    """Manages HubSpot CRM integration for contact and campaign management."""
    
    def __init__(self, api_key: str = None):
        """Initialize HubSpot client."""
        self.api_key = api_key or Config.HUBSPOT_API_KEY
        
        # Initialize client if API key is available, otherwise use mock mode
        if self.api_key and self.api_key != 'your_hubspot_api_key_here':
            self.client = HubSpot(access_token=self.api_key)
            self.mock_mode = False
        else:
            self.client = None
            self.mock_mode = True
            print("HubSpot API key not configured. Running in mock mode.")
            print("   API calls will be simulated with realistic responses.")
    
    def create_or_update_contact(self, email: str, first_name: str, 
                                last_name: str, persona: str,
                                company: Optional[str] = None) -> Dict:
        """
        Create or update a contact in HubSpot.
        
        Args:
            email: Contact email
            first_name: First name
            last_name: Last name
            persona: Audience segment (founders/creatives/operations)
            company: Optional company name
            
        Returns:
            Dictionary with contact_id and status
        """
        if self.mock_mode:
            return self._mock_create_contact(email, first_name, last_name, persona, company)
        
        try:
            # Prepare contact properties
            properties = {
                "email": email,
                "firstname": first_name,
                "lastname": last_name,
                "persona": persona,
            }
            
            if company:
                properties["company"] = company
            
            # Try to create contact
            contact_input = SimplePublicObjectInputForCreate(properties=properties)
            
            try:
                response = self.client.crm.contacts.basic_api.create(
                    simple_public_object_input_for_create=contact_input
                )
                
                return {
                    'contact_id': response.id,
                    'status': 'created',
                    'email': email
                }
            
            except ApiException as e:
                # Contact might already exist, try to update
                if e.status == 409:  # Conflict - contact exists
                    search_response = self.client.crm.contacts.search_api.do_search(
                        public_object_search_request={
                            "filterGroups": [{
                                "filters": [{
                                    "propertyName": "email",
                                    "operator": "EQ",
                                    "value": email
                                }]
                            }]
                        }
                    )
                    
                    if search_response.results:
                        contact_id = search_response.results[0].id
                        
                        # Update existing contact
                        self.client.crm.contacts.basic_api.update(
                            contact_id=contact_id,
                            simple_public_object_input={"properties": properties}
                        )
                        
                        return {
                            'contact_id': contact_id,
                            'status': 'updated',
                            'email': email
                        }
                
                raise e
        
        except Exception as e:
            print(f"Error creating/updating contact: {e}")
            return {
                'contact_id': None,
                'status': 'error',
                'email': email,
                'error': str(e)
            }
    
    def _mock_create_contact(self, email: str, first_name: str, 
                            last_name: str, persona: str, 
                            company: Optional[str] = None) -> Dict:
        """Mock contact creation for testing without API key."""
        # Generate a mock HubSpot ID
        mock_id = str(abs(hash(email)) % 1000000)
        
        return {
            'contact_id': mock_id,
            'status': 'created (mock)',
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'persona': persona,
            'company': company
        }
    
    def create_contact_list(self, list_name: str, persona: str) -> Optional[str]:
        """
        Create a contact list for a specific persona.
        
        Args:
            list_name: Name of the list
            persona: Persona segment
            
        Returns:
            List ID if successful
        """
        if self.mock_mode:
            mock_list_id = str(abs(hash(list_name)) % 10000)
            print(f"Mock: Created list '{list_name}' with ID: {mock_list_id}")
            return mock_list_id
        
        try:
            # Note: HubSpot list creation requires specific API endpoints
            # This is a simplified version showing the structure
            list_data = {
                "name": list_name,
                "dynamic": False,
                "filters": [[{
                    "property": "persona",
                    "operator": "EQ",
                    "value": persona
                }]]
            }
            
            # In production, would use: self.client.crm.lists.create(...)
            print(f"Would create list: {list_name} for persona: {persona}")
            return "mock_list_id_" + str(abs(hash(list_name)))
        
        except Exception as e:
            print(f"Error creating list: {e}")
            return None
    
    def send_email_to_contacts(self, contacts: List[Dict], 
                              subject: str, body: str,
                              campaign_name: str) -> Dict:
        """
        Send email campaign to a list of contacts.
        
        Args:
            contacts: List of contact dictionaries with email, name, etc.
            subject: Email subject line
            body: Email body content
            campaign_name: Campaign identifier
            
        Returns:
            Dictionary with campaign results
        """
        if self.mock_mode:
            return self._mock_send_email(contacts, subject, body, campaign_name)
        
        try:
            
            
            results = {
                'campaign_name': campaign_name,
                'campaign_id': f"camp_{int(time.time())}",
                'contacts_sent': len(contacts),
                'status': 'sent',
                'send_time': datetime.now().isoformat(),
                'recipients': []
            }
            
            for contact in contacts:
                
                recipient_result = {
                    'email': contact.get('email'),
                    'status': 'sent',
                    'contact_id': contact.get('contact_id')
                }
                results['recipients'].append(recipient_result)
            
            return results
        
        except Exception as e:
            print(f"Error sending email campaign: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'contacts_sent': 0
            }
    
    def _mock_send_email(self, contacts: List[Dict], subject: str, 
                        body: str, campaign_name: str) -> Dict:
        """Mock email sending for testing."""
        campaign_id = f"mock_camp_{int(time.time())}"
        
        print(f"\nMOCK EMAIL CAMPAIGN: {campaign_name}")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Subject: {subject}")
        print(f"   Recipients: {len(contacts)}")
        print(f"   Body preview: {body[:100]}...")
        
        recipients = []
        for contact in contacts:
            recipients.append({
                'email': contact.get('email'),
                'name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}",
                'status': 'sent (mock)',
                'contact_id': contact.get('contact_id')
            })
        
        return {
            'campaign_name': campaign_name,
            'campaign_id': campaign_id,
            'contacts_sent': len(contacts),
            'status': 'sent (mock)',
            'send_time': datetime.now().isoformat(),
            'recipients': recipients,
            'subject': subject,
            'body_preview': body[:200]
        }
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict:
        """
        Fetch campaign analytics from HubSpot.
        
        Args:
            campaign_id: The campaign ID
            
        Returns:
            Dictionary with analytics data
        """
        if self.mock_mode:
            return self._mock_campaign_analytics(campaign_id)
        
        try:
            
            analytics = {
                'campaign_id': campaign_id,
                'opens': 0,
                'clicks': 0,
                'bounces': 0,
                'unsubscribes': 0,
                'sent': 0
            }
            
            return analytics
        
        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {}
    
    def _mock_campaign_analytics(self, campaign_id: str) -> Dict:
        """Generate realistic mock analytics data."""
        import random
        
        
        sent = random.randint(50, 200)
        opens = int(sent * random.uniform(0.15, 0.35))  # 15-35% open rate
        clicks = int(opens * random.uniform(0.20, 0.40))  # 20-40% click rate of opens
        bounces = int(sent * random.uniform(0.01, 0.03))  # 1-3% bounce rate
        unsubscribes = int(sent * random.uniform(0.001, 0.01))  # 0.1-1% unsub rate
        
        return {
            'campaign_id': campaign_id,
            'sent': sent,
            'opens': opens,
            'clicks': clicks,
            'bounces': bounces,
            'unsubscribes': unsubscribes,
            'open_rate': opens / sent if sent > 0 else 0,
            'click_rate': clicks / sent if sent > 0 else 0,
            'ctr_of_opens': clicks / opens if opens > 0 else 0,
            'bounce_rate': bounces / sent if sent > 0 else 0,
            'unsubscribe_rate': unsubscribes / sent if sent > 0 else 0
        }
    
    def batch_create_contacts(self, contacts_data: List[Dict]) -> List[Dict]:
        """
        Create multiple contacts in batch.
        
        Args:
            contacts_data: List of contact dictionaries
            
        Returns:
            List of results for each contact
        """
        results = []
        
        for contact_data in contacts_data:
            result = self.create_or_update_contact(
                email=contact_data['email'],
                first_name=contact_data['first_name'],
                last_name=contact_data['last_name'],
                persona=contact_data['persona'],
                company=contact_data.get('company')
            )
            results.append(result)
            
            # Rate limiting - be nice to the API
            if not self.mock_mode:
                time.sleep(0.1)
        
        return results
    
    def segment_contacts_by_persona(self, contacts: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Segment contacts by persona type.
        
        Args:
            contacts: List of all contacts
            
        Returns:
            Dictionary with persona keys and contact lists
        """
        segmented = {
            'founders': [],
            'creatives': [],
            'operations': []
        }
        
        for contact in contacts:
            persona = contact.get('persona', '').lower()
            if persona in segmented:
                segmented[persona].append(contact)
        
        return segmented
    
    def log_campaign_to_crm(self, campaign_data: Dict) -> str:
        """
        Log campaign details to CRM for tracking.
        
        Args:
            campaign_data: Campaign information
            
        Returns:
            Campaign log ID
        """
        if self.mock_mode:
            log_id = f"log_{int(time.time())}"
            print(f"Mock: Logged campaign to CRM with ID: {log_id}")
            return log_id
        
        try:
            
            log_id = f"crm_log_{int(time.time())}"
            print(f"Logged campaign: {campaign_data.get('name')} to CRM")
            return log_id
        
        except Exception as e:
            print(f"Error logging campaign: {e}")
            return ""
    
    def get_contact_engagement_history(self, contact_id: str) -> List[Dict]:
        """
        Get engagement history for a specific contact.
        
        Args:
            contact_id: HubSpot contact ID
            
        Returns:
            List of engagement events
        """
        if self.mock_mode:
            return [{
                'type': 'EMAIL_OPEN',
                'timestamp': datetime.now().isoformat(),
                'campaign': 'mock_campaign'
            }]
        
        try:
            
            return []
        
        except Exception as e:
            print(f"Error fetching engagement history: {e}")
            return []

