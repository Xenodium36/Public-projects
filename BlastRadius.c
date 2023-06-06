#include <stdlib.h>
#include <stdio.h>
#include <math.h>


float getScaledDistance(float weight, float distance)
{
    float cubeRootOfChargeWeight = pow(weight, 0.3333333);
    return distance / cubeRootOfChargeWeight;
}

float calculateIncidentPressure(float t)
{
    float U = -0.214362789151 + 1.35034249993 * t;
    float ip = 2.78076916577 - 1.6958988741 * U -
               0.154159376846 * pow(U, 2) +
               0.514060730593 * pow(U, 3) +
               0.0988534365274 * pow(U, 4) -
               0.293912623038 * pow(U, 5) -
               0.0268112345019 * pow(U, 6) +
               0.109097496421 * pow(U, 7) +
               0.00162846756311 * pow(U, 8) -
               0.0214631030242 * pow(U, 9) +
               0.0001456723382 * pow(U, 10) +
               0.00167847752266 * pow(U, 11);
    ip = pow(10, ip);
    return ip;
}

float calculateReflectedPressure(float t)
{
    float U = -0.240657322658 + 1.36637719229 * t;
    float rp = 3.40283217581 - 2.21030870597 * U -
               0.218536586295 * pow(U, 2) +
               0.895319589372 * pow(U, 3) +
               0.24989009775 * pow(U, 4) -
               0.569249436807 * pow(U, 5) -
               0.11791682383 * pow(U, 6) +
               0.224131161411 * pow(U, 7) +
               0.0245620259375 * pow(U, 8) -
               0.0455116002694 * pow(U, 9) -
               0.00190930738887 * pow(U, 10) +
               0.00361471193389 * pow(U, 11);
    rp = pow(10, rp);
    return rp;
}

float calculateTimeOfArrival(float impulse, float t)
{
    float cubeRootOfChargeWeight = pow(impulse, 0.3333333);
    float U = -0.202425716178 + 1.37784223635 * t;
    float toa = -0.0591634288046 + 1.35706496258 * U +
                0.052492798645 * pow(U, 2) -
                0.196563954086 * pow(U, 3) -
                0.0601770052288 * pow(U, 4) +
                0.0696360270891 * pow(U, 5) +
                0.0215297490092 * pow(U, 6) -
                0.0161658930785 * pow(U, 7) -
                0.00232531970294 * pow(U, 8) +
                0.00147752067524 * pow(U, 9);
    toa = pow(10, toa);
    toa = toa * cubeRootOfChargeWeight;
    return toa;
}

float calculateShockFrontVelocity(float t)
{
    float U = -0.202425716178 + 1.37784223635 * t;
    float sv = -0.06621072854 - 0.698029762594 * U +
               0.158916781906 * pow(U, 2) +
               0.443812098136 * pow(U, 3) -
               0.113402023921 * pow(U, 4) -
               0.369887075049 * pow(U, 5) +
               0.129230567449 * pow(U, 6) +
               0.19857981197 * pow(U, 7) -
               0.0867636217397 * pow(U, 8) -
               0.0620391900135 * pow(U, 9) +
               0.0307482926566 * pow(U, 10) +
               0.0102657234407 * pow(U, 11) -
               0.00546533250772 * pow(U, 12) -
               0.000693180974 * pow(U, 13) +
               0.0003847494916 * pow(U, 14);
    sv = pow(10, sv) * 1000;
    return sv;
}

float getPressure(float z)
{
    return 93.2 / z + 383 / pow(z, 2) + 1275 / pow(z, 3);
}

float maxFireballSize(float power)
{
    return (145 * pow(power, 0.39)) / 3.28084;
}

double maxFBSizeReached(float power, float radius)
{
    float e = power * 4.184 * pow(10, 12);
    float r = pow(radius, 5);
    double t = pow((r * 1.2) / e, 0.5);
    return t * 1000;
}

float getScaledMINRange(float weight){
    float cubeRootOfChargeWeight = pow(weight,0.3333333);
    return 0.0674 * cubeRootOfChargeWeight; 
}

float getScaledMAXRange(float weight){
    float cubeRootOfChargeWeight = pow(weight,0.3333333);
    return 40 * cubeRootOfChargeWeight;  
}

void printHint()
{
    printf("Optimal height of explosion (m):\n");
    printf("\tTheorists believe that the maximum full destruction of a nuclear warhead is at an overpressure value of 20PSI.\n");
    printf("\tThis value is achieved with a 1KT bomb at an altitude of 220m above the ground.\n");
    printf("\tWe can convert this value to the necessary power of an atomic bomb using the formula.\n\n");

    printf("Maximum theoretical size of fireball (m):\n");
    printf("\tFireball is the core of the explosion\n");
    printf("\tUsing the formula you can theoretically calculate its radius\n\n");

    printf("Maximum fireball size theoretically reached at time (ms):\n");
    printf("\tThe formula can be used to estimate when the fireball reaches its maximum radius.\n\n");

    printf("Distance:\n");
    printf("\tThe distance traveled by the pressure wave from the explosion in a given time.\n");
    printf("\tThe calculation with the given equations is valid only up to a distance of 400m.\n\n");

    printf("Incident pressure (kPa):\n");
    printf("\tIs the force of a pressure wave at a certain distance\n");
    printf("\tDependence of pressure and damage to buildings:\n");
    printf("\t\t> 83 kPa  -> Totall destruction\n");
    printf("\t\t> 35 kPa  -> Serious damage\n");
    printf("\t\t> 17 kPa  -> Medium damage\n");
    printf("\t\t> 3,5 kPa -> Light damage\n\n");

    printf("Reflected pressure (kPa):\n");
    printf("\tIf the incident pressure is reflected from an object, a reflected pressure wave is created.\n");
    printf("\tThis pressure wave is often more dangerous than the incident pressure wave.\n\n");

    printf("Time of arrival (ms):\n");
    printf("\tThe time it takes for a pressure wave to reach a given distance.\n");

    printf("Shock front velocity (m/s):\n");
    printf("\tThe velocity of the pressure wave at a given distance from the explosion.\n\n");
}

void calculate(float distance, float weight, float impulse, float t, float incidentPressure)
{
    printf("---------------------------------------------------------\n");
    printf("| Incident pressure\t\t\t| %.3f kPa\t|\n", incidentPressure);

    float p = getPressure(getScaledDistance(weight, distance));
    printf("---------------------------------------------------------\n");
    printf("| Incident pressure (another approach)\t| %.3f kPa\t|\n", p);

    float reflectedPressure = calculateReflectedPressure(t);
    printf("---------------------------------------------------------\n");
    printf("| Reflected pressure\t\t\t| %.3f kPa\t|\n", reflectedPressure);

    float timeOfArrival = calculateTimeOfArrival(impulse, t);
    printf("---------------------------------------------------------\n");
    printf("| Time of arrival\t\t\t| %.2f ms\t|\n", timeOfArrival);

    float shockFrontVelocity = calculateShockFrontVelocity(t);
    printf("---------------------------------------------------------\n");
    printf("| Shock front velocity\t\t\t| %.2f m/s\t|\n", shockFrontVelocity);
    printf("---------------------------------------------------------\n\n");
}

float getArea(float r1, float r2){
    float s1 = 3.14 * pow(r1, 2);
    float s2 = 3.14 * pow(r2, 2);
    float s3 = s2 - s1;

    return s3/1000000;
}

int main()
{

    printf("This is a simulation of the theoretical destruction of an atomic bomb\n");
    printf("You can use ctrl + c to end this program anytime you want\n");
    printf("Do you wish to get explanation of calculated variables? \n[y/n][Y/N]\n");
    int c;
    int int1 = 0, int2 = 0, int3 = 0, int4 = 0;
    do
    {
        c = getchar();
    } while (c != 'y' && c != 'Y' && c != 'n' && c != 'N');

    if (c == 'y' || c == 'Y')
        printHint();

    float weight, power, distance, impulse, optimalHeight, fireBallSize, t;
    double maxSizeReachedAt;
    float incidentPressure;
    float intervalStart = 0;
    float maxPressure;
    float minRange, maxRange;
    int total, serious, medium, light;

    while (1)
    {
        printf("Please enter the power of the atomic bomb in KT\n");
        printf("1KT = 1000 Tons of TNT\n");
        scanf("%f", &power);
        printf("#####################################################\n");
        printf("\tThe calculation runs for a %dKT bomb\n", (int)power);
        printf("#####################################################\n");
        weight = power * 1000;
        impulse = weight;
        minRange = getScaledMINRange(weight);
        maxRange = getScaledMAXRange(weight);

        optimalHeight = pow(power, 0.3333333) * 220;
        printf("---------------------------------------------------------------------------------\n");
        printf("| Optimal height of explosion for maximal destruction \t| %.2f m\t\t|\n", optimalHeight);
        fireBallSize = maxFireballSize(power);
        printf("---------------------------------------------------------------------------------\n");
        printf("| Maximal theoretical radius of fireball:\t\t| %.2f m\t\t|\n", fireBallSize);
        maxSizeReachedAt = maxFBSizeReached(power, fireBallSize);
        printf("---------------------------------------------------------------------------------\n");
        printf("| Maximal theoretical area of fireball:\t\t\t| %.2f km^2\t\t|\n", (3.14 * pow(fireBallSize,2))/100000);
        printf("---------------------------------------------------------------------------------\n");
        printf("| Maximal fireball size theoretically reached at:\t| %.2f ms\t\t|\n", maxSizeReachedAt);
        printf("---------------------------------------------------------------------------------\n\n");

        for (distance = minRange; distance < maxRange; distance = distance + 0.01)
        {
            t = log(getScaledDistance(weight, distance)) / log(10);
            incidentPressure = calculateIncidentPressure(t);
            if (distance >= minRange && distance <= (minRange + 0.01))
                maxPressure = incidentPressure;
            if (incidentPressure <= 83.0 && int1 == 0)
            {
                printf("---------------------------------------------------------\n");
                printf("|-----------------Totall destruction--------------------|\n");
                printf("---------------------------------------------------------\n");
                printf("| Distance\t\t\t\t| %dm - %dm\t|\n", (int)intervalStart, (int)distance);
                printf("---------------------------------------------------------\n");
                printf("| Area of damage\t\t\t| %.4fkm^2\t|\n", getArea(intervalStart, distance));
                intervalStart = distance;
                total = (int)distance;
                total = (int)(total / 5);
                calculate(distance, weight, impulse, t, incidentPressure);
                int1 = 1;
            }
            else if (incidentPressure <= 35.0 && int2 == 0)
            {
                printf("---------------------------------------------------------\n");
                printf("|--------------------Serious damage---------------------|\n");
                printf("---------------------------------------------------------\n");
                printf("| Distance\t\t\t\t| %dm - %dm\t|\n", (int)intervalStart, (int)distance);
                printf("---------------------------------------------------------\n");
                printf("| Area of damage\t\t\t| %.4fkm^2\t|\n", getArea(intervalStart, distance));
                intervalStart = distance;
                serious = (int)distance;
                serious = (int)(serious / 5);
                serious = serious - total;
                calculate(distance, weight, impulse, t, incidentPressure);
                int2 = 2;
            }
            else if (incidentPressure <= 17.0 && int3 == 0)
            {
                printf("---------------------------------------------------------\n");
                printf("|--------------------Medium damage----------------------|\n");
                printf("---------------------------------------------------------\n");
                printf("| Distance\t\t\t\t| %dm - %dm\t|\n", (int)intervalStart, (int)distance);
                printf("---------------------------------------------------------\n");
                printf("| Area of damage\t\t\t| %.4fkm^2\t|\n", getArea(intervalStart, distance));
                intervalStart = distance;
                medium = (int)distance;
                medium = (int)(medium / 5);
                medium = medium - serious;
                calculate(distance, weight, impulse, t, incidentPressure);
                int3 = 1;
            }
            else if (incidentPressure <= 3.5 && int4 == 0)
            {
                printf("---------------------------------------------------------\n");
                printf("|---------------------Light damage----------------------|\n");
                printf("---------------------------------------------------------\n");
                printf("| Distance\t\t\t\t| %dm - %dm\t|\n", (int)intervalStart, (int)distance);
                printf("---------------------------------------------------------\n");
                printf("| Area of damage\t\t\t| %.4fkm^2\t|\n", getArea(intervalStart, distance));
                calculate(distance, weight, impulse, t, incidentPressure);
                light = (int)distance;
                light = (int)(light / 5);
                light = light - medium;
                int4 = 1;
            }
        }
        printf("---------------------------------------------------------\n");
        printf("| Maximum incident pressure: \t| %.4f kPa\t|\n", maxPressure);
        printf("---------------------------------------------------------\n\n");

        printf("Do you wish to calculate another explosion?\n[y/n][Y/N]\n");
        do
        {
            c = getchar();
        } while (c != 'y' && c != 'Y' && c != 'n' && c != 'N');

        if (c == 'n' || c == 'N')
            break;
        printf("\n\n\n");
        int1 = 0; int2 = 0; int3 = 0; int4 = 0;
        intervalStart = 0;
    }
    printf("\n\nBye\n\n");
    return 0;
}