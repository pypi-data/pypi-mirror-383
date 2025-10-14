from django.db import connection
from apps.src.models import SpUsers
import logging

logger = logging.getLogger(__name__)


# Alternative optimized version using database recursive query (if your DB supports it)
def get_all_subordinates_optimized(user_id):
    """
    Get all subordinates using a more efficient database query approach
    
    Args:
        user_id: Primary key of the user
        
    Returns:
        list: List of distinct user IDs (primary keys) of all subordinates
    """
    try:
        user_id = int(user_id)

        # Verify user exists
        if not SpUsers.objects.filter(id=user_id).exists():
            return []

        # Use raw SQL for recursive query (MySQL 8.0+ syntax)
        # MySQL supports WITH RECURSIVE since version 8.0
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE subordinate_hierarchy AS (
                    -- Base case: direct subordinates
                    SELECT id, reporting_to_id, 1 as level
                    FROM sp_users 
                    WHERE reporting_to_id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: subordinates of subordinates
                    SELECT u.id, u.reporting_to_id, sh.level + 1
                    FROM sp_users u
                    INNER JOIN subordinate_hierarchy sh ON u.reporting_to_id = sh.id
                    WHERE sh.level < 10  -- Prevent infinite recursion
                )
                SELECT DISTINCT id FROM subordinate_hierarchy
                ORDER BY id;
            """, [user_id])

            result = cursor.fetchall()
            return [row[0] for row in result]

    except Exception as e:
        logger.error(f"Error in optimized subordinate query for user {user_id}: {str(e)}")
        logger.error(f"Falling back to iterative approach")
        # Fallback to the iterative approach
        return []



# Alternative optimized version using database recursive query (if your DB supports it)
def get_all_distributors(user_ids):
    try:
        # Use raw SQL for recursive query (MySQL 8.0+ syntax)
        # MySQL supports WITH RECURSIVE since version 8.0
        with connection.cursor() as cursor:
            query = f"""
                select id, first_name, last_name, emp_sap_id, store_name,
                    latitude, longitude, reporting_to_emp_id
                from sp_users where user_type = 2 and reporting_to_emp_id in ({user_ids})
            """
            cursor.execute(query)

            # result = cursor.fetchall()
            # logger.info(f"Optimized subordinate query result for user {user_ids}: {result}")
            return get_dictfetchall(cursor)

    except Exception as e:
        logger.error(f"Error in optimized subordinate query for user {user_ids}: {str(e)}")
        logger.error(f"Falling back to iterative approach")
        # Fallback to the iterative approach
        return None


def get_dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]



def get_last_locations(user_ids, start_date, end_date):
    logger.info(f"Fetching last locations for user IDs {user_ids} between {start_date} and {end_date}")
    try:
        # Use raw SQL for recursive query (MySQL 8.0+ syntax)
        # MySQL supports WITH RECURSIVE since version 8.0
        with connection.cursor() as cursor:
            query = f"""
                SELECT t.user_id, t.latitude, t.longitude, t.sync_date_time
                FROM sp_user_tracking t
                INNER JOIN (
                    SELECT user_id, MAX(created_at) AS max_created_at
                    FROM sp_user_tracking
                    WHERE user_id IN ({user_ids})
                    AND created_at >= '{start_date}'
                    AND created_at < '{end_date}'
                    GROUP BY user_id
                ) AS latest
                ON t.user_id = latest.user_id AND t.created_at = latest.max_created_at;

            """
            cursor.execute(query)

            # result = cursor.fetchall()
            # logger.info(f"Optimized subordinate query result for user {user_ids}: {result}")
            return get_dictfetchall(cursor)

    except Exception as e:
        logger.info(f"Error in optimized last location query for user {user_ids}: {str(e)}")
        logger.info(f"Falling back to iterative approach")
        # Fallback to the iterative approach
        return None
