# @author Daniel McCoy Stephenson
"""Every key that may be set on State.flags, in one place.

A flag is something that happened this winter and that nothing forgets: a
choice someone will hold you to, a thing done to the station, a report
sent. There is no reset in Overwinter, so a flag is for good - which is
what makes "X will remember that" mean something here. The dict stays
free-form in the save file (schemas/save.json allows any object), but the
game only ever writes these names, so a typo is an import error rather
than a silent no-op.
"""

# Choices people hold you to - see Scene.remember.
KEPT_MARITS_SECRET = "keptMaritsSecret"  # True: kept it; False: told her you wouldn't
TOLD_DOV = "toldDov"  # Dov knows there are five
DOV_HOLDS = "dovHolds"  # Dov chose not to send it
DOV_REPORTED = "dovReported"  # Dov sent it; the dark flight is coming
TOLD_MARIT_ABOUT_TEO = "toldMaritAboutTeo"
COVERED_FOR_TEO = "coveredForTeo"
BROUGHT_AKSEL_IN = "broughtAkselIn"
LEFT_AKSEL_AT_HUT = "leftAkselAtHut"
BACKED_AKSEL_STAYING = "backedAkselStaying"

# Things done to the station.
MARIT_APPROVED_HALF = "maritApprovedHalf"  # half rations may be set
HALF_RATIONS = "halfRations"
DEPOT_FETCHED = "depotFetched"
DEPOT_LEAD_FROM_MARIT = "depotLeadFromMarit"
MET_TEO = "metTeo"  # Teo has talked to you once; the fuel check is offered
GENERATOR_RAN_DRY = "generatorRanDry"  # the storm night, and Dov's hour lost
STORE_EMPTIED_ON = "storeEmptiedOn"  # the day the store hit zero, if it did
AKSEL_WALKED_IN = "akselWalkedIn"  # he came to the station on his own
HUNTED_TODAY = "huntedToday"  # one seal a day, at most
PLANE_ON_STRIP = "planeOnStrip"  # the last morning
AKSEL_ASKED_TO_STAY = "akselAskedToStay"

ALL = (
    KEPT_MARITS_SECRET,
    TOLD_DOV,
    DOV_HOLDS,
    DOV_REPORTED,
    TOLD_MARIT_ABOUT_TEO,
    COVERED_FOR_TEO,
    BROUGHT_AKSEL_IN,
    LEFT_AKSEL_AT_HUT,
    BACKED_AKSEL_STAYING,
    MARIT_APPROVED_HALF,
    HALF_RATIONS,
    DEPOT_FETCHED,
    DEPOT_LEAD_FROM_MARIT,
    MET_TEO,
    GENERATOR_RAN_DRY,
    STORE_EMPTIED_ON,
    AKSEL_WALKED_IN,
    HUNTED_TODAY,
    PLANE_ON_STRIP,
    AKSEL_ASKED_TO_STAY,
)
