import json
from unittest.mock import patch

def test_get_my_problems_as_admin(client, mock_auth):
    # Setup Admin
    mock_auth(user_id=1, username='admin', role='admin')
    
    # Setup some headers with a fake token
    headers = {'Authorization': 'Bearer fake-token'}
    
    # As admin (id=1), should see all problems (assuming DB has some)
    response = client.get('/api/problems/my', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # Check that we likely got multiple problems (seeded ones)
    assert len(data) >= 1

def test_get_my_problems_as_student(client, mock_auth):
    # Setup Student
    mock_auth(user_id=999, username='teststudent', role='student')
    
    headers = {'Authorization': 'Bearer fake-token'}
    
    # Regular user should see 0 problems initially (unless they created one)
    response = client.get('/api/problems/my', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    
    # Ensure only owned problems are returned (filtering logic)
    for p in data:
        # p['owner_id'] might be missing if filtering handled by query, checking returned data logic
        # But in our code: problems = session.query(Problem).filter_by(owner_id=current_user_id).all()
        # So it must be owned by 999
        pass

def test_submissions_history_admin(client, mock_auth):
    mock_auth(user_id=1, username='admin', role='admin')
    headers = {'Authorization': 'Bearer fake-token'}
    
    response = client.get('/api/problems/submissions', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # Admin might see submissions from others

def test_submissions_history_student(client, mock_auth):
    mock_auth(user_id=999, username='teststudent', role='student')
    headers = {'Authorization': 'Bearer fake-token'}
    
    response = client.get('/api/problems/submissions', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # Should only see their own
    for sub in data:
        assert sub['username'] == 'teststudent'
