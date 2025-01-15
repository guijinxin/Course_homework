from typing import List

from langchain_core.tools import StructuredTool


# 模拟课程数据
courses = [
    {"id": 1, "name": "Introduction to Computer Science", "type": "必修", "description": "基础计算机科学课程"},
    {"id": 2, "name": "Data Structures", "type": "必修", "description": "数据结构与算法"},
    {"id": 3, "name": "Database Systems", "type": "选修", "description": "数据库设计与管理"},
    {"id": 4, "name": "Software Engineering", "type": "选修", "description": "软件开发流程与方法"},
    {"id": 5, "name": "Advanced Programming", "type": "选修", "description": "高级编程技术"},
    {"id": 6, "name": "Sports and Health", "type": "选修", "description": "体育与健康"},
    {"id": 7, "name": "Badminton", "type": "选修", "description": "羽毛球课程"},
]

# 用户已选课程
selected_courses = []

def query_courses(course_type: str = None, keyword: str = None) -> dict:
    """
    查询课程，支持按类型和关键词筛选
    :param course_type: 课程类型（必修/选修）
    :param keyword: 关键词
    :return: 符合条件的课程列表（dict 格式）
    """
    result = courses.copy()
    
    if course_type:
        result = [course for course in result if course["type"] == course_type]
    
    if keyword:
        result = [course for course in result if keyword.lower() in course["description"].lower()]
    
    return {
        "status": "success",
        "data": result
    }

def select_course(course_name: str) -> dict:
    """
    选课
    :param course_name: 课程名称
    :return: 选课结果（dict 格式）
    """
    course = next((course for course in courses if course["name"].lower() == course_name.lower()), None)
    
    if not course:
        return {
            "status": "error",
            "message": "课程不存在，请检查课程名称。"
        }
    
    if course in selected_courses:
        return {
            "status": "error",
            "message": "您已经选择了这门课程。"
        }
    
    selected_courses.append(course)
    return {
        "status": "success",
        "message": f"成功选择课程: {course['name']}"
    }

def delete_course(course_name: str) -> dict:
    """
    删除已选课程
    :param course_name: 课程名称
    :return: 删除结果（dict 格式）
    """
    course = next((course for course in selected_courses if course["name"].lower() == course_name.lower()), None)
    
    if not course:
        return {
            "status": "error",
            "message": "您没有选择这门课程，无法删除。"
        }
    
    selected_courses.remove(course)
    return {
        "status": "success",
        "message": f"成功删除课程: {course['name']}"
    }

def list_selected_courses() -> dict:
    """
    列出已选课程
    :return: 已选课程列表（dict 格式）
    """
    return {
        "status": "success",
        "data": selected_courses
    }

query_courses_tool=StructuredTool.from_function(
    func=query_courses,
    name="查询课程",
    description="查询课程，支持按类型和关键词筛选"
)

select_course_tool=StructuredTool.from_function(
    func=select_course,
    name="选课",
    description="选课。返回选课结果"
)

delete_course_tool=StructuredTool.from_function(
    func=delete_course,
    name="退课",
    description="删除已选课程,返回选课结果"
)
list_selected_courses_tool=StructuredTool.from_function(
    func=list_selected_courses,
    name="列出已选课程",
    description="列出已选课程。返回已选课程列表"
)

tools = [query_courses_tool,select_course_tool, delete_course_tool, list_selected_courses_tool]