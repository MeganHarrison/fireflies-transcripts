"""
Set up projects in Supabase for better meeting assignment
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_sample_projects():
    """Create sample projects based on the meetings we've seen"""
    
    projects = [
        {
            "name": "Goodwill Bloomington",
            "description": "Goodwill store project in Bloomington",
            "keywords": ["goodwill", "bloomington", "gw", "morning", "meeting"],
            "team_members": [
                "participant1@goodwill.org",
                "participant2@goodwill.org"
            ],
            "status": "active"
        },
        {
            "name": "Niemann Foods Integration",
            "description": "Niemann Foods and FedEx Office projects",
            "keywords": ["niemann", "foods", "fedex", "office", "carmel", "weekly"],
            "team_members": [
                "participant1@niemann.com",
                "participant2@alleato.com"
            ],
            "status": "active"
        },
        {
            "name": "Exotec Air System",
            "description": "Exotec air system questions and integration",
            "keywords": ["exotec", "air", "questions", "system"],
            "team_members": [
                "engineer1@exotec.com",
                "engineer2@exotec.com"
            ],
            "status": "active"
        },
        {
            "name": "Daily Standups",
            "description": "Daily TB meetings and standups",
            "keywords": ["daily", "tb", "standup", "sync"],
            "team_members": [
                "team@company.com"
            ],
            "status": "active"
        },
        {
            "name": "Uniqlo Integration",
            "description": "Uniqlo and Alleato group projects",
            "keywords": ["uniqlo", "alleato", "group"],
            "team_members": [
                "uniqlo@alleato.com"
            ],
            "status": "active"
        }
    ]
    
    print("🚀 Creating sample projects...\n")
    
    created = 0
    for project in projects:
        try:
            # Check if project already exists
            existing = supabase.table("projects").select("id").eq("name", project["name"]).execute()
            
            if existing.data:
                print(f"⏩ Project '{project['name']}' already exists")
            else:
                result = supabase.table("projects").insert(project).execute()
                print(f"✅ Created project: {project['name']}")
                created += 1
                
        except Exception as e:
            print(f"❌ Error creating project '{project['name']}': {e}")
    
    print(f"\n📊 Summary: Created {created} new projects")
    
    # Show all projects
    all_projects = supabase.table("projects").select("*").execute()
    print(f"\n📋 Total projects in database: {len(all_projects.data)}")
    
    for proj in all_projects.data:
        print(f"\n🏢 {proj['name']}")
        print(f"   ID: {proj['id']}")
        print(f"   Keywords: {', '.join(proj.get('keywords', []))}")
        print(f"   Team: {len(proj.get('team_members', []))} members")


def reassign_meetings():
    """Reassign existing meetings to appropriate projects"""
    
    print("\n\n🔄 Reassigning meetings to projects...")
    
    # Get all meetings
    meetings = supabase.table("meetings").select("*").execute()
    projects = supabase.table("projects").select("*").execute()
    
    reassigned = 0
    
    for meeting in meetings.data:
        title = meeting['title'].lower()
        current_project = meeting.get('project_id')
        
        # Find best matching project
        best_match = None
        best_score = 0
        
        for project in projects.data:
            score = 0
            
            # Check keywords
            for keyword in project.get('keywords', []):
                if keyword.lower() in title:
                    score += 2  # Higher weight for title matches
            
            # Special cases
            if "goodwill" in title and "goodwill" in project['name'].lower():
                score += 5
            elif "niemann" in title and "niemann" in project['name'].lower():
                score += 5
            elif "exotec" in title and "exotec" in project['name'].lower():
                score += 5
            elif "daily tb" in title and "daily" in project['name'].lower():
                score += 5
            elif "uniqlo" in title and "uniqlo" in project['name'].lower():
                score += 5
            
            if score > best_score:
                best_score = score
                best_match = project
        
        # Update if we found a better match
        if best_match and (not current_project or best_score > 3):
            try:
                supabase.table("meetings").update({
                    "project_id": best_match['id']
                }).eq("id", meeting['id']).execute()
                
                print(f"✅ Reassigned '{meeting['title']}' to '{best_match['name']}' (score: {best_score})")
                reassigned += 1
            except Exception as e:
                print(f"❌ Error reassigning meeting: {e}")
        else:
            print(f"⏩ '{meeting['title']}' - keeping current assignment")
    
    print(f"\n📊 Reassigned {reassigned} meetings")


if __name__ == "__main__":
    # Create projects
    create_sample_projects()
    
    # Reassign meetings
    reassign_meetings()
    
    print("\n✅ Project setup complete!")