## Project 7 — SpaceTech Satellite Data Summariser

<table>
	<tr>
		<th align="left">Sector</th>
		<td>SpaceTech / Satellite Intelligence</td>
	</tr>
	<tr>
		<th align="left">Problem</th>
		<td>Space operations analysts need to quickly compile intelligence reports on specific satellites — combining orbital telemetry from tracking APIs, recent mission news, and technical specifications. Currently done manually, taking hours. We automate it with an agent.</td>
	</tr>
	<tr>
		<th align="left">Solution</th>
		<td>A LangChain ReAct agent with 4 tools: satellite data retrieval (mock API), web search (Tavily), orbital calculations, and report formatting. The agent autonomously determines what to search for and which tools to call.</td>
	</tr>
	<tr>
		<th align="left">Stack</th>
		<td>LangChain, OpenAI GPT-4o-mini, Tavily, FastAPI, Pydantic V2, Poetry</td>
	</tr>
	<tr>
		<th align="left">Duration</th>
		<td>105 minutes (14:00 — 15:45)</td>
	</tr>
	<tr>
		<th align="left">Deliverable</th>
		<td>FastAPI service at http://localhost:8004 — POST /satellite-report accepts a satellite name and returns a structured intelligence report</td>
	</tr>
</table>

## Project 8 — eCommerce Smart Shopper Agent

<table>
	<tr>
		<th align="left">Sector</th>
		<td>eCommerce / Retail</td>
	</tr>
	<tr>
		<th align="left">Problem</th>
		<td>Users want personalised product recommendations based on real-time prices, reviews, and availability — not static catalogue data.</td>
	</tr>
	<tr>
		<th align="left">Solution</th>
		<td>A LangChain agent that uses Tavily to search for real-time product listings, compares using structured criteria, and returns ranked recommendations with justification.</td>
	</tr>
	<tr>
		<th align="left">Stack</th>
		<td>LangChain, Tavily, OpenAI GPT-4o-mini, FastAPI, Pydantic V2</td>
	</tr>
	<tr>
		<th align="left">Duration</th>
		<td>60 minutes (15:45 — 16:45)</td>
	</tr>
	<tr>
		<th align="left">Deliverable</th>
		<td>FastAPI service at http://localhost:8005 — POST /recommend takes shopping query, returns ranked products with reasoning</td>
	</tr>
</table>
