"""
Update project assignments for meetings based on title matching
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def show_current_assignments():
    """Show current meeting-project assignments"""
    
    print("📊 Current Meeting Assignments:\n")
    
    meetings = supabase.table("meetings").select("*, project:projects(name)").order("date", desc=True).execute()
    
    for meeting in meetings.data:
        project_name = meeting.get('project', {}).get('name', 'Not Assigned') if meeting.get('project') else 'Not Assigned'
        print(f"📄 {meeting['title']}")
        print(f"   → Project: {project_name}")
        print(f"   → Project ID: {meeting.get('project_id', 'None')}")
        print()


def suggest_better_assignments():
    """Suggest better project assignments based on title matching"""
    
    print("\n🔍 Analyzing for better assignments...\n")
    
    meetings = supabase.table("meetings").select("*").execute()
    projects = supabase.table("projects").select("*").execute()
    
    suggestions = []
    
    for meeting in meetings.data:
        title_lower = meeting['title'].lower()
        current_project_id = meeting.get('project_id')
        
        # Find all matching projects
        matches = []
        
        for project in projects.data:
            project_name_lower = project['name'].lower()
            score = 0
            
            # Direct name matching
            if "goodwill bloomington" in title_lower and "goodwill bloomington" in project_name_lower:
                score = 10
            elif "goodwill" in title_lower and "goodwill" in project_name_lower:
                score = 5
            elif "niemann" in title_lower and "niemann" in project_name_lower:
                score = 8
            elif "exotec" in title_lower and "exotec" in project_name_lower:
                score = 8
            elif "uniqlo" in title_lower and "uniqlo" in project_name_lower:
                score = 8
            
            # Partial matching
            title_words = set(title_lower.split())
            project_words = set(project_name_lower.split())
            common_words = title_words & project_words
            
            # Ignore common words
            common_words -= {'the', 'and', 'or', 'in', 'at', 'to', 'for', 'of', 'a', 'an'}
            
            if common_words:
                score += len(common_words) * 2
            
            if score > 0:
                matches.append((project, score))
        
        # Sort by score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        if matches and matches[0][1] > 2:
            best_project = matches[0][0]
            if best_project['id'] != current_project_id:
                suggestions.append({
                    'meeting': meeting,
                    'current_project_id': current_project_id,
                    'suggested_project': best_project,
                    'score': matches[0][1]
                })
    
    # Show suggestions
    if suggestions:
        print("💡 Suggested reassignments:\n")
        for s in suggestions:
            current = "Not Assigned"
            if s['current_project_id']:
                for p in projects.data:
                    if p['id'] == s['current_project_id']:
                        current = p['name']
                        break
            
            print(f"📄 {s['meeting']['title']}")
            print(f"   Current: {current}")
            print(f"   Suggested: {s['suggested_project']['name']} (confidence: {s['score']}/10)")
            print()
        
        # Ask to apply
        response = input("\n🤔 Apply these suggestions? (y/n): ")
        
        if response.lower() == 'y':
            applied = 0
            for s in suggestions:
                try:
                    supabase.table("meetings").update({
                        "project_id": s['suggested_project']['id']
                    }).eq("id", s['meeting']['id']).execute()
                    applied += 1
                except Exception as e:
                    print(f"❌ Error updating meeting: {e}")
            
            print(f"\n✅ Applied {applied} reassignments")
    else:
        print("✅ No better assignments found - current assignments look good!")


def manual_assignment():
    """Manually assign a meeting to a project"""
    
    print("\n📝 Manual Assignment\n")
    
    # Show meetings
    meetings = supabase.table("meetings").select("*").order("date", desc=True).execute()
    
    print("Meetings:")
    for i, meeting in enumerate(meetings.data):
        print(f"{i+1}. {meeting['title']}")
    
    meeting_idx = int(input("\nSelect meeting number: ")) - 1
    
    # Show projects
    projects = supabase.table("projects").select("*").order("name").execute()
    
    print("\nProjects:")
    for i, project in enumerate(projects.data):
        print(f"{i+1}. {project['name']}")
    
    project_idx = int(input("\nSelect project number: ")) - 1
    
    # Update
    try:
        supabase.table("meetings").update({
            "project_id": projects.data[project_idx]['id']
        }).eq("id", meetings.data[meeting_idx]['id']).execute()
        
        print(f"\n✅ Assigned '{meetings.data[meeting_idx]['title']}' to '{projects.data[project_idx]['name']}'")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    while True:
        print("\n" + "="*60)
        print("🏢 Project Assignment Manager")
        print("="*60)
        print("1. Show current assignments")
        print("2. Suggest better assignments")
        print("3. Manual assignment")
        print("4. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            show_current_assignments()
        elif choice == "2":
            suggest_better_assignments()
        elif choice == "3":
            manual_assignment()
        elif choice == "4":
            break
        else:
            print("Invalid option")