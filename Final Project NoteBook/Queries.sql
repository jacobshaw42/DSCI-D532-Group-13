/*1.NULL values*/

SELECT 
	uD.name 
FROM 
	userDim uD 
INNER JOIN 
	healthFact hF on uD.id = hF.user_id
WHERE 
	hF.value IS NULL;

-----------------------------------------------------
/*
2.mean median
3.max min and count of data
*/

SELECT 
    hF.user_id,
    dD.Year,
	hD.type
    AVG(hF.value) AS 'Average/Mean',
    MAX(hF.value) AS 'Maximum value for the Year',
    MIN(hF.value) AS 'Minimum value for the Year',
   ((MAX(hF.value) + MIN(hF.value)) / 2) AS 'Median'
FROM 
    healthFact hF 
INNER JOIN 
    dateDim dD ON hF.date_id = dD.id
INNER JOIN 
    healthDim hD ON hF.healthData_id = hD.id	
GROUP BY 
    hF.user_id,
	dD.Year,
	hD.type;

