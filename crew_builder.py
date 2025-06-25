from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool

import os
search_tool = SerperDevTool()



def create_crew(prompt):
    llm = LLM(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="gemini/gemini-2.5-flash"

    )

    response_generator = Agent(
        role="Senior Response Generator",
        goal=f"Generate a comprehensive, well-researched response to {prompt} that is accurate, clear, and directly addresses the user's needs",
        backstory=("""You are an expert response generator with years of experience creating helpful, accurate content. 
                    Your mission is to craft responses that are informative, well-structured, and directly relevant to the user's query.

                    Guidelines for your responses:
                    - Use web search to verify facts and get current information
                    - Structure your response logically with clear sections
                    - Include specific examples when helpful
                    - Aim for completeness while staying focused
                    - Write in a professional yet accessible tone

                    Your workflow:
                    1. First, you'll generate an initial response
                    2. A Senior Critic will review it and provide feedback
                    3. You'll then revise your response based on the critic's suggestions
                    4. Finally, a Response Improvement Officer will add final polish

                    When revising, carefully consider the critic's feedback and implement suggestions that improve accuracy, clarity, and                             usefulness."""),
        llm = llm,
        allow_delegation= False,
        verbose = True,
        tools=[search_tool]
    )


    critic = Agent(
        role = "Senior Critic",
        goal = f"Provide constructive critique and suggestions to improve the response of the Senior Response Generator to improve the response to : {prompt} ",
        backstory= ("""You are a meticulous Senior Critic with expertise in content evaluation and improvement. 
                    Your role is to thoroughly review responses and identify areas for enhancement.

                    Focus your critique on:
                    - **Accuracy**: Verify facts, check for outdated information, identify missing context
                    - **Completeness**: Note gaps in coverage, missing perspectives, or unanswered aspects
                    - **Logic & Structure**: Assess flow, organization, and argument coherence
                    - **Relevance**: Ensure the response directly addresses the user's specific needs
                    - **Clarity**: Identify confusing sections or areas needing simplification

                    Format your feedback as:
                    1. Strengths of the current response
                    2. Specific issues with suggested solutions
                    3. Priority recommendations for improvement

                    Use web search to fact-check claims and verify current information."""),
        llm = llm,
        verbose= True,
        allow_delegation= True,
        tools=[search_tool]
    )

    improver= Agent(
        role = "Senior Response Improvement Officer",
        goal= f"Polish the final response that Senior Critic and the Senior Response Generater created and fixed after receiving prompt:                        {prompt}",
        backstory=("""You are a skilled Response Improvement Officer specializing in content refinement and presentation. 
                    You receive a response that has been critiqued and your job is to create the final, polished version.

                    Your focus areas:
                    - **Integration**: Seamlessly incorporate critic's feedback and suggestions
                    - **Flow & Readability**: Ensure smooth transitions and clear progression
                    - **Formatting**: Optimize structure, headings, and visual organization
                    - **Tone Consistency**: Maintain professional yet approachable voice throughout
                    - **Final Quality Check**: Ensure accuracy, completeness, and user value

                    Your output should be the definitive response ready for the user - clear, comprehensive, and highly useful.
                    Use web search if you need to verify any final details or add current information."""),
        llm = llm,
        verbose = True,
        allow_delegation=False,
        tools=[search_tool]
    )


    generate_task= Task(
        description=f"Generate an initial comprehensive response to {prompt}",
        agent = response_generator,
        expected_output="A well structured informative response with verified facts and clear explanations"
    )

    critique_task=Task(
        description=(f"""Review and critique the response generated for:{prompt}
                     Analyze the generated response and provide specific, actionable feedback on:
                     -Accuracy and factual correctness
                     -Completeness and coverage
                     -Structure and clarity
                     -Relevance to original prompt

                     The respnse to critique:{generate_task.output}
                     Provide clear, specific suggestions that the generator can implement. """),
        agent=critic,
        expected_output="Detailed feedback with specifc suggestions for improvement, organized by priority",
        context=[generate_task]



    )

    fix_task=Task(
        description=(f""" Revise the original response to:{prompt}
                     Take your original response and the critic's feedback, then created an improved version that addresses the critic's suggestions.

                     Original response: {generate_task.output}
                     Critic's feedback: {critique_task.output}

                     Implmenet the suggestions you agree with and improve the response accordingly"""),
        agent=response_generator,
        expected_output="Revises response that incorporates the critic's feedback and addresses identified issues",
        context=[generate_task,critique_task]
    )

    improve_task = Task(
        description=f""" Create the final polished response for: {prompt}
                    Take the generator's revised response and add final polish and refinement.

                    Revised Response: {fix_task.output}

                    Focus on:
                    -Final formatting and presentation.
                    -Flow and readability optimization
                    -Consistency in tone and style
                    -Any final quality enhancements""",
        agent=improver,
        expected_output="Final, polished response ready for user consumption",
        context=[fix_task]
    )


    crew= Crew(
        agents=[response_generator, critic,improver],
        tasks=[generate_task,critique_task,fix_task,improve_task],
        verbose=True
    )

    return crew