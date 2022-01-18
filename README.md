# streetnameLinks

This project is dedicated to linking street names to the person they are named after.
The street information is taken from OpenStreetMap and linked to person data that was generated using Wikidata (as at May 17th 2022).

Our method was tested on streets from the city of Bremen and the state of North Rhine-Westfalia in Germany. It was able to detect 896 new person links in Bremen and 31.363 new links in North Rhine-Westfalia respectively.

You can take a look at the findings of this project in best_candidate_bremen.csv or best_candidate_nrw.csv.

If you want to link streets from a different region, you will have to generate the candidates for said streets using street_candidates.py.
You can then use predict.py to pick the most likely person from the candidates for each street
