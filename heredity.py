import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def calculate_num_genes(person, one_gene, two_genes):
    """
    Calculate the number of genes for a person based on the input sets one_gene and two_genes.
    """
    if person in two_genes:
        return 2
    elif person in one_gene:
        return 1
    else:
        return 0


def calculate_gene_pass_probability(parent, one_gene, two_genes):
    """
    Calculate the probability of a parent passing genes to their child.
    """
    if parent in two_genes:
        return 1 - PROBS["mutation"]
    elif parent in one_gene:
        return 0.5
    else:
        return PROBS["mutation"]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """
    probability = 1.0

    for person in people:
        num_genes = calculate_num_genes(person, one_gene, two_genes)
        has_trait = person in have_trait
        mother = people[person]["mother"]
        father = people[person]["father"]

        if mother is None and father is None:
            probability *= PROBS["gene"][num_genes]
        else:
            gene_pass_probabilities = {
                parent: calculate_gene_pass_probability(parent, one_gene, two_genes)
                for parent in [mother, father]
            }

            # Calculate gene passing probabilities for mother and father
            mother_prob = gene_pass_probabilities[mother]
            father_prob = gene_pass_probabilities[father]

            # Calculate probabilities based on the number of genes
            if num_genes == 2:
                probability *= mother_prob * father_prob
            elif num_genes == 1:
                probability *= mother_prob * (1 - father_prob) + (1 - mother_prob) * father_prob
            else:
                probability *= (1 - mother_prob) * (1 - father_prob)

        probability *= PROBS["trait"][num_genes][has_trait]

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Update the probabilities dictionary with the new joint distribution probability.
    """
    for person in probabilities:
        if person in two_genes:
            genes = 2
        elif person in one_gene:
            genes = 1
        else:
            genes = 0

        trait = person in have_trait

        probabilities[person]["gene"][genes] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Normalize the probabilities dictionary to ensure each distribution sums to 1.
    """
    for person in probabilities:
        # Normalize gene distribution
        total_gene_prob = sum(probabilities[person]["gene"].values())
        for gene_count in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene_count] /= total_gene_prob

        # Normalize trait distribution
        total_trait_prob = sum(probabilities[person]["trait"].values())
        for has_trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][has_trait] /= total_trait_prob


if __name__ == "__main__":
    main()
