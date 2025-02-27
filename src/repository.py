# Third party imports
import logging
from typing import Dict, List

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session, joinedload

# Internal imports
from src.models import Aircraft, AircraftData
from src.schemas import (AircraftBaseSchema, AircraftDataUpdateSchema,
                         AircraftDisplaySchema, AircraftUpdateSchema)
from src.exceptions import DatabaseIntegrityError, InvalidDataError, AircraftNotFoundError, AircraftRepositoryError

logger = logging.getLogger(__name__)


class AircraftRepository:
    """
    Repository class to manage operations related to the Aircraft and AircraftData tables.

    Attributes:
        session (Session): The SQLAlchemy session used for database transactions.

    Methods:
        add_aircraft(aircraft: AircraftBaseSchema) -> AircraftDisplaySchema:
            Adds a new aircraft to the database.
        display_aircrafts() -> List[AircraftDisplaySchema]:
            Retrieves and returns all aircraft in the database.
        update_aircraft(aircraft_id: int, **kwargs) -> AircraftUpdateSchema:
            Updates an existing aircraft based on the provided aircraft_id and field values.
        delete_aircraft(aircraft_id: int) -> None:
            Deletes the aircraft with the given aircraft_id from the database.
    """

    def __init__(self, session: Session):
        """
        Initializes AircraftRepository class.

        Arguments:
            session: SQLAlchemy session object.
        """
        self.session = session

    def is_present(self, aircraft_id: int) -> bool:
        """
        Checks if an aircraft with the given aircraft_id exists in the database.

        Arguments:
            aircraft_id {int} -- The aircraft object id.

        Returns:
            bool: True if the aircraft exists, otherwise False.
        """
        exist = select(exists().where(Aircraft.aircraft_id == aircraft_id))
        result = self.session.execute(exist).scalar_one_or_none()

        return bool(result)

    def add_aircraft(self, aircraft: AircraftBaseSchema) -> AircraftDisplaySchema:
        """
        Adds new Aircraft instance to the database.

        Arguments:
            aircraft: instance of Aircraft class to be added using the AircraftBaseSchema.

        Returns:
            Instance of the Aircraft class displayed according to AircraftDisplaySchema.
        """
        try:
            new_aircraft = Aircraft(**aircraft.model_dump(exclude={"aircraft_data"}))
            new_aircraft_data = AircraftData(**aircraft.aircraft_data.model_dump(), aircraft=new_aircraft)
            self.session.add_all([new_aircraft, new_aircraft_data])
            self.session.commit()

            logger.info("Aircraft added successfully.")
            added_aircraft = self.session.query(Aircraft).options(
                joinedload(Aircraft.aircraft_data)).order_by(Aircraft.aircraft_id.desc()).first()

            return AircraftDisplaySchema.model_validate(added_aircraft)

        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error adding aircraft: {str(e)}")
            raise DatabaseIntegrityError

        except Exception as e:
            logger.error(f"Unexpected error adding aircraft: {str(e)}")
            raise InvalidDataError(message=str(e))

    def display_aircrafts(self) -> List[AircraftDisplaySchema]:
        """
        Returns all the aircraft in the database as a list, contains
        the Aircraft objects, using the AircraftDisplaySchema.
        """
        all_aircrafts = self.session.query(Aircraft).options(joinedload(Aircraft.aircraft_data)).all()
        if not all_aircrafts:
            logger.warning("No aircraft found in the database.")

        return [AircraftDisplaySchema.model_validate(aircraft) for aircraft in all_aircrafts]

    def update_aircraft(self, aircraft_id: int, **kwargs) -> AircraftUpdateSchema | None:
        """
        Finds the aircraft instance based on the given 'id',
        and updates the elements given as a keywords arguments.

        Arguments:
            aircraft_id: id of the Aircraft instance to be updated.
            **kwargs: keyword arguments to be updated using the AircraftUpdateSchema.

        Returns:
            Aircraft object based on the AircraftUpdateSchema.
        """
        if self.is_present(aircraft_id=aircraft_id):

            try:
                ac_values = AircraftUpdateSchema(
                    **kwargs).model_dump(exclude={"aircraft_data"}, exclude_none=True)
                ac_data_values = AircraftDataUpdateSchema(
                    **kwargs.get("aircraft_data", {})).model_dump(exclude_none=True)

                if not ac_values and not ac_data_values:
                    raise InvalidDataError("No valid aircraft update data provided. "
                                           "Ensure that at least one field is populated.")

                with self.session.begin():
                    if ac_values:
                        self.session.query(Aircraft).filter_by(
                            aircraft_id=aircraft_id).update(values={**ac_values})

                    if ac_data_values:
                        self.session.query(AircraftData).filter_by(
                            aircraft_id=aircraft_id).update(values={**ac_data_values})

                updated_aircraft = {**ac_values, "aircraft_data": {**ac_data_values}}
                logger.info(f"Aircraft with id {aircraft_id} updated successfully.")

                return AircraftUpdateSchema.model_validate(updated_aircraft)

            except NoResultFound as e:
                logger.error(f"Aircraft with id {aircraft_id} not found: {str(e)}")
                raise AircraftNotFoundError

            except IntegrityError as e:
                self.session.rollback()
                logger.error(f"Integrity error updating aircraft: {str(e)}")
                raise DatabaseIntegrityError(str(e))

            except Exception as e:
                logger.error(f"Unexpected error updating aircraft: {str(e)}")
                raise AircraftRepositoryError(str(e))

    def delete_aircraft(self, aircraft_id: int) -> Dict[str, str] | None:
        """
        Deletes the aircraft instance of given 'id' from the database.

        Arguments:
              aircraft_id (int): The 'id' of the Aircraft to delete.

        Returns:
                Dict[str, str]: A confirmation message.
        """
        try:
            if self.is_present(aircraft_id=aircraft_id):
                with self.session.begin():
                    self.session.query(Aircraft).filter_by(aircraft_id=aircraft_id).delete()
                    logger.info(f"Aircraft with id {aircraft_id} deleted successfully.")

                return {"message": f"Aircraft with id {aircraft_id} deleted successfully."}

        except NoResultFound:
            logger.error("Aircraft not found.")
            raise AircraftNotFoundError(f"Aircraft with id {aircraft_id} not found.")

        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error deleting aircraft: {str(e)}")
            raise DatabaseIntegrityError(str(e))

        except Exception as e:
            logger.error(f"Unexpected error deleting aircraft: {str(e)}")
            raise AircraftRepositoryError(str(e))
