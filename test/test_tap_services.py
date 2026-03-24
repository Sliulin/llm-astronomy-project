from astroquery.gaia import Gaia

# 设置查询
query = """
SELECT TOP 10 *
FROM gaiadr3.gaia_source
WHERE CONTAINS(
    POINT('ICRS', ra, dec), 
    CIRCLE('ICRS', 83.633333, 6.550000, 0.1)
)=1
"""

# 执行查询
job = Gaia.launch_job(query)
results = job.get_results()
print(results)